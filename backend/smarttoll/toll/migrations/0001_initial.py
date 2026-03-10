from django.db import migrations, models
import uuid
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="TollBooth",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("booth_name", models.CharField(max_length=100)),
                ("location_description", models.TextField(blank=True)),
                ("camera_rtsp_url", models.TextField(blank=True)),
                ("is_operational", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="VehicleClass",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("class_name", models.CharField(max_length=50, unique=True)),
                ("toll_rate", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="VideoUpload",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("file_name", models.CharField(blank=True, max_length=255)),
                ("file", models.FileField(upload_to="uploads/")),
                ("processing_status", models.CharField(choices=[("PENDING", "Pending"), ("PROCESSING", "Processing"), ("COMPLETED", "Completed"), ("FAILED", "Failed")], default="PENDING", max_length=20)),
                ("upload_timestamp", models.DateTimeField(auto_now_add=True)),
                ("completion_timestamp", models.DateTimeField(blank=True, null=True)),
                ("log", models.TextField(blank=True)),
                (
                    "uploaded_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="auth.user"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="VehicleLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("confidence_score", models.FloatField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("snapshot_image", models.ImageField(blank=True, null=True, upload_to="detections/")),
                (
                    "booth",
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="toll.tollbooth"),
                ),
                (
                    "source_video",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="toll.videoupload"),
                ),
                (
                    "vehicle_class",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="toll.vehicleclass"),
                ),
            ],
            options={"indexes": [models.Index(fields=["timestamp"], name="toll_vehicl_timesta_9c3fbd_idx"), models.Index(fields=["vehicle_class"], name="toll_vehicl_vehicle_046a1d_idx"), models.Index(fields=["booth"], name="toll_vehicl_booth__b1b081_idx")]},
        ),
        migrations.CreateModel(
            name="DailyAudit",
            fields=[
                ("audit_date", models.DateField(primary_key=True, serialize=False)),
                ("total_vehicles_count", models.IntegerField(default=0)),
                ("total_revenue_estimated", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ("peak_traffic_hour", models.IntegerField(blank=True, null=True)),
                ("generated_at", models.DateTimeField(auto_now_add=True)),
                ("report_pdf", models.FileField(blank=True, null=True, upload_to="reports/")),
            ],
        ),
    ]
