from django.urls import path
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import VehicleLog, DailyAudit, VideoUpload, VehicleClass, TollBooth
from .serializers import VideoUploadSerializer, VehicleClassSerializer
from .tasks import process_video_upload_task, generate_daily_audit_task

User = get_user_model()

router = routers.DefaultRouter()


@api_view(["GET"])
@permission_classes([AllowAny])
def vehicle_classes(request):
    """Return all configured vehicle classes with toll rates."""
    qs = VehicleClass.objects.filter(is_active=True).order_by("id")
    serializer = VehicleClassSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def live_stats(request):
    """Aggregated counts for today, broken down by vehicle class."""
    now = timezone.now()
    today = now.date()
    logs_today = VehicleLog.objects.filter(timestamp__date=today)
    total_today = logs_today.count()

    per_class = list(
        logs_today
        .values("vehicle_class__id", "vehicle_class__class_name")
        .annotate(count=Count("id"))
        .order_by("vehicle_class__id")
    )

    # Fill in zero-count classes so the frontend always gets all classes
    active_classes = VehicleClass.objects.filter(is_active=True).order_by("id")
    counted_ids = {item["vehicle_class__id"] for item in per_class}
    for vc in active_classes:
        if vc.id not in counted_ids:
            per_class.append({
                "vehicle_class__id": vc.id,
                "vehicle_class__class_name": vc.class_name,
                "count": 0,
            })
    per_class.sort(key=lambda x: x["vehicle_class__id"])

    # Estimated revenue
    revenue = sum(
        item["count"] * float(VehicleClass.objects.get(id=item["vehicle_class__id"]).toll_rate)
        for item in per_class
    )

    return Response({
        "date": str(today),
        "total": total_today,
        "revenue_estimated": round(revenue, 2),
        "by_class": per_class,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def hourly_stats(request):
    today = timezone.now().date()
    hourly = [
        VehicleLog.objects.filter(timestamp__date=today, timestamp__hour=h).count()
        for h in range(24)
    ]
    return Response({"date": str(today), "hourly": hourly})


@api_view(["GET"])
@permission_classes([AllowAny])
def recent_events(request):
    """Return the most recent vehicle crossing events (last 50)."""
    limit = int(request.query_params.get("limit", 50))
    limit = min(limit, 200)
    logs = (
        VehicleLog.objects
        .select_related("vehicle_class", "booth")
        .order_by("-timestamp")[:limit]
    )
    data = [
        {
            "id": str(log.id),
            "vehicle_class": log.vehicle_class.class_name,
            "vehicle_class_id": log.vehicle_class.id,
            "confidence": round(log.confidence_score, 3),
            "booth": log.booth.booth_name if log.booth else None,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]
    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def upload_video(request):
    """
    Upload video for processing
    Allows both authenticated and unauthenticated users for demo purposes
    """
    serializer = VideoUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Handle both authenticated and unauthenticated users
    if request.user.is_authenticated:
        instance = serializer.save(uploaded_by=request.user)
    else:
        # For anonymous users, assign to demo user
        demo_user, _ = User.objects.get_or_create(
            username='demo_user', 
            defaults={'is_staff': False, 'is_active': True}
        )
        instance = serializer.save(uploaded_by=demo_user)
    
    # Trigger async task processing
    result = process_video_upload_task.delay(str(instance.id))
    return Response({
        "id": str(instance.id), 
        "status": instance.processing_status, 
        "task_id": str(result.id) if hasattr(result, 'id') else None,
        "message": "Video upload started. Processing in background..."
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def upload_status(request):
    upload_id = request.query_params.get("id")
    if not upload_id:
        return Response({"error": "id query param required"}, status=400)
    try:
        upload = VideoUpload.objects.get(id=upload_id)
        return Response({
            "id": str(upload.id),
            "status": upload.processing_status,
            "file_name": upload.file_name,
            "log": upload.log,
            "upload_timestamp": upload.upload_timestamp,
            "completion_timestamp": upload.completion_timestamp,
        })
    except VideoUpload.DoesNotExist:
        return Response({"error": "upload not found"}, status=404)


@api_view(["GET"])
@permission_classes([AllowAny])
def export_audit(request):
    date = request.query_params.get("date")
    if date:
        generate_daily_audit_task.delay(date)
        return Response({"status": "queued", "date": date})
    return Response({"error": "date query param required YYYY-MM-DD"}, status=400)


urlpatterns = [
    path("vehicle-classes/", vehicle_classes),
    path("stats/live/", live_stats),
    path("stats/hourly/", hourly_stats),
    path("events/recent/", recent_events),
    path("upload/video/", upload_video),
    path("upload/status/", upload_status),
    path("audit/export/", export_audit),
]
