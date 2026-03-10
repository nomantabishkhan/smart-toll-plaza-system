from django.urls import path
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import VehicleLog, DailyAudit, VideoUpload, VehicleClass, TollBooth
from .serializers import VideoUploadSerializer
from .tasks import process_video_upload_task, generate_daily_audit_task

User = get_user_model()

router = routers.DefaultRouter()


@api_view(["GET"])
@permission_classes([AllowAny])
def live_stats(request):
    now = timezone.now()
    today = now.date()
    total_today = VehicleLog.objects.filter(timestamp__date=today).count()
    per_class = (
        VehicleLog.objects.filter(timestamp__date=today)
        .values("vehicle_class__class_name")
        .annotate(count=Count("id"))
    )
    return Response({"total": total_today, "by_class": list(per_class)})


@api_view(["GET"])
@permission_classes([AllowAny])
def hourly_stats(request):
    today = timezone.now().date()
    hourly = [
        VehicleLog.objects.filter(timestamp__date=today, timestamp__hour=h).count()
        for h in range(24)
    ]
    return Response({"date": str(today), "hourly": hourly})


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
    path("stats/live/", live_stats),
    path("stats/hourly/", hourly_stats),
    path("upload/video/", upload_video),
    path("upload/status/", upload_status),
    path("audit/export/", export_audit),
]
