import uuid
from django.db import models


class TollBooth(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booth_name = models.CharField(max_length=100)
    location_description = models.TextField(blank=True)
    camera_rtsp_url = models.TextField(blank=True)
    is_operational = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.booth_name


class VehicleClass(models.Model):
    id = models.IntegerField(primary_key=True)  # map to model class index
    class_name = models.CharField(max_length=50, unique=True)
    toll_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.class_name


class VideoUpload(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to="uploads/")
    uploaded_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    progress = models.IntegerField(default=0)  # 0-100 %
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    completion_timestamp = models.DateTimeField(null=True, blank=True)
    log = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.file_name


class VehicleLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booth = models.ForeignKey(TollBooth, null=True, on_delete=models.SET_NULL)
    vehicle_class = models.ForeignKey(VehicleClass, on_delete=models.PROTECT)
    confidence_score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    snapshot_image = models.ImageField(upload_to="detections/", null=True, blank=True)
    source_video = models.ForeignKey(VideoUpload, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["vehicle_class"]),
            models.Index(fields=["booth"]),
        ]

    def __str__(self) -> str:
        return f"{self.vehicle_class} @ {self.timestamp}"


class DailyAudit(models.Model):
    audit_date = models.DateField(primary_key=True)
    total_vehicles_count = models.IntegerField(default=0)
    total_revenue_estimated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    peak_traffic_hour = models.IntegerField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    report_pdf = models.FileField(upload_to="reports/", null=True, blank=True)

    def __str__(self) -> str:
        return f"Audit {self.audit_date}"
