from rest_framework import serializers
from .models import TollBooth, VehicleClass, VehicleLog, VideoUpload, DailyAudit


class VehicleClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleClass
        fields = "__all__"


class TollBoothSerializer(serializers.ModelSerializer):
    class Meta:
        model = TollBooth
        fields = "__all__"


class VehicleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleLog
        fields = "__all__"


class VideoUploadSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        file = validated_data.get("file")
        if file and not validated_data.get("file_name"):
            validated_data["file_name"] = getattr(file, "name", "upload")
        return super().create(validated_data)

    class Meta:
        model = VideoUpload
        fields = "__all__"
        extra_kwargs = {
            "uploaded_by": {"required": False},
        }
        read_only_fields = ["uploaded_by", "processing_status", "upload_timestamp", "completion_timestamp", "log"]


class DailyAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAudit
        fields = "__all__"
