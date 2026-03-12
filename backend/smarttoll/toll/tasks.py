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


@shared_task
def process_video_upload_task(video_upload_id: str):
    """
    Process uploaded video for vehicle detection
    Falls back to DEMO MODE if YOLO unavailable
    Runs asynchronously in Celery worker
    """
    try:
        upload = VideoUpload.objects.get(id=video_upload_id)
        upload.processing_status = "PROCESSING"
        upload.log = "Starting video processing..."
        upload.save(update_fields=["processing_status", "log"])

        if not os.path.exists(upload.file.path):
            raise FileNotFoundError(f"Video file not found: {upload.file.path}")

        cap = cv2.VideoCapture(upload.file.path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {upload.file.path}")
        
        booth = TollBooth.objects.first()
        if not booth:
            booth = TollBooth.objects.create(booth_name="Default Booth", location_description="Auto-created")
        
        yolo_model = _get_yolo_model()
        use_demo_mode = yolo_model is None
        if not use_demo_mode:
            upload.log = "YOLO loaded. Running AI inference..."
            upload.save(update_fields=["log"])
        else:
            upload.log = "Using DEMO MODE (simulated detections)"
            upload.save(update_fields=["log"])
        
        frame_count = 0
        total_detections = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_skip = max(1, int(fps))
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            frame_count += 1
            
            if frame_count % frame_skip != 0:
                continue
            
            try:
                if use_demo_mode:
                    detections = []
                    num_detections = random.randint(1, 3)
                    for _ in range(num_detections):
                        class_id = random.randint(0, 7)
                        confidence = random.uniform(0.85, 0.98)
                        detections.append({'class_id': class_id, 'confidence': confidence})
                else:
                    detections = []
                    results = yolo_model(frame, conf=0.30, verbose=False)
                    for result in results:
                        if getattr(result, "boxes", None) is None:
                            continue
                        for box in result.boxes:
                            class_id = int(box.cls[0].item())
                            confidence = float(box.conf[0].item())
                            detections.append({"class_id": class_id, "confidence": confidence})
                
                for detection in detections:
                    class_id = detection['class_id']
                    confidence = detection['confidence']
                    vehicle_class = VehicleClass.objects.filter(id=class_id).first()
                    
                    if vehicle_class:
                        VehicleLog.objects.create(
                            booth=booth,
                            vehicle_class=vehicle_class,
                            confidence_score=confidence,
                            source_video=upload,
                        )
                        total_detections += 1

                        # Push real-time event to WebSocket clients
                        try:
                            broadcast_vehicle_detected(
                                vehicle_class_name=vehicle_class.class_name,
                                confidence=confidence,
                                booth_name=booth.booth_name if booth else "",
                            )
                        except Exception:
                            pass  # Don't let broadcast failures break processing
                
            except Exception:
                logger.exception("Frame inference failed for upload %s", video_upload_id)
                continue
        
        cap.release()
        
        upload.processing_status = "COMPLETED"
        upload.completion_timestamp = timezone.now()
        mode_str = "[DEMO]" if use_demo_mode else "[YOLO]"
        upload.log = f"{mode_str} Processed {frame_count} frames, detected {total_detections} vehicles"
        upload.save(update_fields=["processing_status", "completion_timestamp", "log"])
        
        generate_daily_audit_task.delay(str(timezone.now().date()))
        
    except Exception as exc:
        logger.exception("Video processing failed for upload %s", video_upload_id)
        VideoUpload.objects.filter(id=video_upload_id).update(
            processing_status="FAILED", 
            log=f"Error: {str(exc)}",
            completion_timestamp=timezone.now()
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
