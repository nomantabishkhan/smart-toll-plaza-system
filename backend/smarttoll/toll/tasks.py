import os
import cv2
import random
import logging
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.utils import timezone

# Lazy import of YOLO to avoid startup issues
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except Exception as e:
    YOLO_AVAILABLE = False
    YOLO_IMPORT_ERROR = str(e)

from .models import VideoUpload, VehicleLog, VehicleClass, DailyAudit, TollBooth
from .broadcast import broadcast_vehicle_detected, broadcast_stats_update

logger = logging.getLogger(__name__)
_MODEL = None


def _get_yolo_model():
    """Lazily load YOLO model; return None if unavailable."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    if not YOLO_AVAILABLE:
        return None

    model_path = getattr(settings, "YOLO_MODEL_PATH", "")
    if not model_path:
        logger.warning("YOLO_MODEL_PATH is not configured. Falling back to demo mode.")
        return None
    if not os.path.exists(model_path):
        logger.warning("YOLO model file not found at %s. Falling back to demo mode.", model_path)
        return None

    try:
        _MODEL = YOLO(model_path)
        return _MODEL
    except Exception:
        logger.exception("Failed to initialize YOLO model. Falling back to demo mode.")
        return None


def _ensure_vehicle_classes():
    """Ensure all 8 vehicle classes exist in the database."""
    CLASSES = [
        (0, "Auto", 30.00),
        (1, "Bus", 100.00),
        (2, "Car", 50.00),
        (3, "LCV", 120.00),
        (4, "Motorcycle", 20.00),
        (5, "Multiaxle", 200.00),
        (6, "Tractor", 80.00),
        (7, "Truck", 150.00),
    ]
    for class_id, name, rate in CLASSES:
        VehicleClass.objects.get_or_create(
            id=class_id,
            defaults={"class_name": name, "toll_rate": rate, "is_active": True},
        )


@shared_task
def process_video_upload_task(video_upload_id: str):
    """
    Process uploaded video for vehicle detection using BoT-SORT tracking.
    Each unique tracked vehicle is logged exactly once (no double-counting).
    Falls back to DEMO MODE if YOLO is unavailable.
    """
    try:
        # Make sure all vehicle classes exist before processing
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

        yolo_model = _get_yolo_model()
        use_demo_mode = yolo_model is None
        if not use_demo_mode:
            upload.log = "YOLO loaded. Running AI inference with BoT-SORT tracking..."
            upload.save(update_fields=["log"])
        else:
            upload.log = "Using DEMO MODE (simulated detections)"
            upload.save(update_fields=["log"])

        frame_count = 0
        total_detections = 0
        # Track unique vehicle IDs so each vehicle is counted exactly once
        seen_track_ids = set()
        # In demo mode, use a counter to simulate unique IDs
        demo_track_counter = 0

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame_count += 1

            try:
                if use_demo_mode:
                    # Simulate tracked detections — ~1 new vehicle every 30 frames
                    if frame_count % int(fps) == 0:
                        num = random.randint(0, 2)
                        for _ in range(num):
                            demo_track_counter += 1
                            class_id = random.randint(0, 7)
                            confidence = random.uniform(0.55, 0.98)
                            vehicle_class = VehicleClass.objects.filter(id=class_id).first()
                            if vehicle_class:
                                VehicleLog.objects.create(
                                    booth=booth,
                                    vehicle_class=vehicle_class,
                                    confidence_score=confidence,
                                    source_video=upload,
                                )
                                total_detections += 1
                                try:
                                    broadcast_vehicle_detected(
                                        vehicle_class_name=vehicle_class.class_name,
                                        confidence=confidence,
                                        booth_name=booth.booth_name,
                                    )
                                except Exception:
                                    pass
                else:
                    # ---- Real YOLO + BoT-SORT tracking ----
                    # Resize to 640px wide for faster CPU inference
                    h, w = frame.shape[:2]
                    if w > 640:
                        scale = 640 / w
                        frame = cv2.resize(frame, (640, int(h * scale)))

                    results = yolo_model.track(
                        frame, conf=0.30, persist=True, tracker="botsort.yaml", verbose=False
                    )
                    for result in results:
                        boxes = getattr(result, "boxes", None)
                        if boxes is None:
                            continue
                        for box in boxes:
                            # Extract tracking ID — skip if tracker lost it
                            track_id_tensor = getattr(box, "id", None)
                            if track_id_tensor is None:
                                continue
                            track_id = int(track_id_tensor[0].item())

                            # Only log each unique vehicle once
                            if track_id in seen_track_ids:
                                continue
                            seen_track_ids.add(track_id)

                            class_id = int(box.cls[0].item())
                            confidence = float(box.conf[0].item())
                            vehicle_class = VehicleClass.objects.filter(id=class_id).first()
                            if vehicle_class:
                                VehicleLog.objects.create(
                                    booth=booth,
                                    vehicle_class=vehicle_class,
                                    confidence_score=confidence,
                                    source_video=upload,
                                )
                                total_detections += 1
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
                    upload.log = f"Processing… {pct}% ({total_detections} vehicles detected)"
                    upload.save(update_fields=["progress", "log"])

            except Exception:
                logger.exception("Frame inference failed for upload %s", video_upload_id)
                continue

        cap.release()

        upload.processing_status = "COMPLETED"
        upload.progress = 100
        upload.completion_timestamp = timezone.now()
        mode_str = "[DEMO]" if use_demo_mode else "[YOLO]"
        upload.log = (
            f"{mode_str} Processed {frame_count} frames, "
            f"detected {total_detections} unique vehicles"
        )
        upload.save(update_fields=["processing_status", "progress", "completion_timestamp", "log"])

        # Trigger daily audit generation
        generate_daily_audit_task.delay(str(timezone.now().date()))

        # Push a final stats refresh to all connected clients
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
    """Generate daily audit report"""
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()
    logs = VehicleLog.objects.filter(timestamp__date=target_date)
    total_count = logs.count()
    revenue = sum(float(log.vehicle_class.toll_rate) for log in logs)
    per_hour = {h: logs.filter(timestamp__hour=h).count() for h in range(24)}
    peak_hour = max(per_hour, key=per_hour.get) if total_count else None
    
    DailyAudit.objects.update_or_create(
        audit_date=target_date,
        defaults={
            "total_vehicles_count": total_count,
            "total_revenue_estimated": revenue,
            "peak_traffic_hour": peak_hour,
            "generated_at": timezone.now(),
        },
    )
    return str(target_date)
