from django.contrib import admin
from .models import TollBooth, VehicleClass, VehicleLog, VideoUpload, DailyAudit

admin.site.register(TollBooth)
admin.site.register(VehicleClass)
admin.site.register(VehicleLog)
admin.site.register(VideoUpload)
admin.site.register(DailyAudit)
