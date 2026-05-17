import os
import cv2
import logging
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.utils import timezone

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
    YOLO_IMPORT_ERROR = None
except Exception as e:
    YOLO_AVAILABLE = False
    YOLO_IMPORT_ERROR = str(e)

from .models import VideoUpload, VehicleLog, VehicleClass, DailyAudit, TollBooth
from .broadcast import broadcast_vehicle_detected, broadcast_stats_update

logger = logging.getLogger(__name__)
_MODEL = None


def _get_yolo_model():
    """
    Load and cache the YOLO model.
    Raises RuntimeError immediately if unavailable — no demo fallback.
    """
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    if not YOLO_AVAILABLE:
        raise RuntimeError(
            f"Ultralytics YOLO could not be imported: {YOLO_IMPORT_ERROR}. "
            "Run: pip install ultralytics"
        )

    model_path = getattr(settings, "YOLO_MODEL_PATH", "")
    if not model_path:
        raise RuntimeError(
            "YOLO_MODEL_PATH is not set in settings or .env. "
            "Add YOLO_MODEL_PATH=../models/best.pt to your .env file."
        )
    if not os.path.exists(model_path):
        raise RuntimeError(
            f"YOLO model file not found at: {model_path}. "
            "Verify the path in YOLO_MODEL_PATH and that best.pt is present."
        )

    _MODEL = YOLO(model_path)
    logger.info("YOLO model loaded from %s", model_path)
    return _MODEL


def _ensure_vehicle_classes():
    """Ensure all 8 vehicle classes exist in the database."""
    CLASSES = [
        (0, "Auto",       30.00),
        (1, "Bus",       100.00),
        (2, "Car",        50.00),
        (3, "LCV",       120.00),
        (4, "Motorcycle", 20.00),
        (5, "Multiaxle", 200.00),
        (6, "Tractor",    80.00),
        (7, "Truck",     150.00),
    ]
    for class_id, name, rate in CLASSES:
        VehicleClass.objects.get_or_create(
            id=class_id,
            defaults={"class_name": name, "toll_rate": rate, "is_active": True},
        )


@shared_task
def process_video_upload_task(video_upload_id: str):
    """
    Process an uploaded video for vehicle detection using YOLO + BoT-SORT tracking.

    Key behaviours:
    - Strict YOLO mode: fails immediately if model is missing, no demo fallback.
    - conf=0.55 + iou=0.45: filters out low-confidence and duplicate detections.
    - Track stability gate (3 frames): ignores ghost/flicker tracks.
    - Each unique track ID is counted exactly once.
    """
    try:
        _ensure_vehicle_classes()

        upload = VideoUpload.objects.get(id=video_upload_id)
        upload.processing_status = "PROCESSING"
        upload.progress = 0
        upload.log = "Starting video processing..."
        upload.save(update_fields=["processing_status", "progress", "log"])

        if not os.path.exists(upload.file.path):
            raise FileNotFoundError(f"Video file not found: {upload.file.path}")

        cap = cv2.VideoCapture(upload.file.path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {upload.file.path}")

        booth = TollBooth.objects.first()
        if not booth:
            booth = TollBooth.objects.create(
                booth_name="Default Booth", location_description="Auto-created"
            )

        # Raises immediately if model is missing or broken
        yolo_model = _get_yolo_model()

        upload.log = "YOLO loaded. Running AI inference with BoT-SORT tracking..."
        upload.save(update_fields=["log"])

        frame_count     = 0
        total_detections = 0

        # Count each unique vehicle exactly once
        seen_track_ids = set()

        # Track how many frames each track ID has been observed
        # A vehicle is only logged after being stable for MIN_TRACK_HITS frames
        track_hit_count = {}
        MIN_TRACK_HITS  = 5

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame_count += 1

            try:
                # Resize to 640 px wide for faster CPU inference
                h, w = frame.shape[:2]
                if w > 640:
                    scale = 640 / w
                    frame = cv2.resize(frame, (640, int(h * scale)))

                results = yolo_model.track(
                    frame,
                    conf=0.72,        # raised from 0.30 — cuts false positives
                    iou=0.45,           # suppresses overlapping duplicate boxes
                    persist=True,
                    tracker="botsort.yaml",
                    verbose=False,
                )

                for result in results:
                    boxes = getattr(result, "boxes", None)
                    if boxes is None:
                        continue

                    for box in boxes:
                        # Skip if tracker lost this object
                        track_id_tensor = getattr(box, "id", None)
                        if track_id_tensor is None:
                            continue

                        track_id = int(track_id_tensor[0].item())

                        # Accumulate frame hits for this track
                        track_hit_count[track_id] = track_hit_count.get(track_id, 0) + 1

                        # Already logged — skip
                        if track_id in seen_track_ids:
                            continue

                        # Not yet stable — skip until seen for MIN_TRACK_HITS frames
                        if track_hit_count[track_id] < MIN_TRACK_HITS:
                            continue

                        # Stable, new vehicle — log it
                        seen_track_ids.add(track_id)

                        class_id   = int(box.cls[0].item())
                        confidence = float(box.conf[0].item())

                        vehicle_class = VehicleClass.objects.filter(id=class_id).first()
                        if not vehicle_class:
                            logger.warning(
                                "Unknown class_id %d detected — skipping.", class_id
                            )
                            continue

                        VehicleLog.objects.create(
                            booth=booth,
                            vehicle_class=vehicle_class,
                            confidence_score=confidence,
                            source_video=upload,
                        )
                        total_detections += 1
                        logger.debug(
                            "Vehicle logged: track_id=%d class=%s conf=%.2f",
                            track_id, vehicle_class.class_name, confidence,
                        )

                        try:
                            broadcast_vehicle_detected(
                                vehicle_class_name=vehicle_class.class_name,
                                confidence=confidence,
                                booth_name=booth.booth_name,
                            )
                        except Exception:
                            pass

                # Progress update every 100 frames
                if frame_count % 100 == 0 and total_frames > 0:
                    pct = min(int(frame_count / total_frames * 100), 99)
                    upload.progress = pct
                    upload.log = (
                        f"Processing… {pct}% "
                        f"({total_detections} vehicles detected so far)"
                    )
                    upload.save(update_fields=["progress", "log"])

            except Exception:
                logger.exception(
                    "Frame inference failed on frame %d for upload %s",
                    frame_count, video_upload_id,
                )
                continue

        cap.release()

        upload.processing_status  = "COMPLETED"
        upload.progress           = 100
        upload.completion_timestamp = timezone.now()
        upload.log = (
            f"[YOLO] Processed {frame_count} frames, "
            f"detected {total_detections} unique vehicles"
        )
        upload.save(update_fields=[
            "processing_status", "progress", "completion_timestamp", "log"
        ])

        generate_daily_audit_task.delay(str(timezone.now().date()))

        try:
            broadcast_stats_update({"refresh": True})
        except Exception:
            pass

    except Exception as exc:
        logger.exception("Video processing failed for upload %s", video_upload_id)
        VideoUpload.objects.filter(id=video_upload_id).update(
            processing_status="FAILED",
            log=f"Error: {str(exc)}",
            completion_timestamp=timezone.now(),
        )


@shared_task
def generate_daily_audit_task(date_str=None):
    """Generate or refresh the daily audit record for the given date."""
    target_date = (
        datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_str
        else timezone.now().date()
    )

    logs        = VehicleLog.objects.filter(timestamp__date=target_date)
    total_count = logs.count()
    revenue     = sum(float(log.vehicle_class.toll_rate) for log in logs)
    per_hour    = {h: logs.filter(timestamp__hour=h).count() for h in range(24)}
    peak_hour   = max(per_hour, key=per_hour.get) if total_count else None

    DailyAudit.objects.update_or_create(
        audit_date=target_date,
        defaults={
            "total_vehicles_count":    total_count,
            "total_revenue_estimated": revenue,
            "peak_traffic_hour":       peak_hour,
            "generated_at":            timezone.now(),
        },
    )
    return str(target_date)