# Quick Developer Reference

## Start Working (60 seconds)

```powershell
cd "d:\pc data\projects\fyp smart toll plaza audit system\backend"
.\.venv\Scripts\activate
python manage.py runserver 127.0.0.1:8000
```

Then open: http://localhost:8000 (login with your superuser)

---

## Common Commands

### Database Operations
```powershell
# Apply migrations
python manage.py migrate

# Create new migration (after editing models.py)
python manage.py makemigrations

# Reset database (DESTRUCTIVE)
rm db.sqlite3
python manage.py migrate
python manage.py shell < populate_classes.py

# Access Django shell
python manage.py shell
```

### Data Management
```powershell
# Populate vehicle classes
python manage.py shell < populate_classes.py

# Create superuser (admin login)
python manage.py createsuperuser

# Access admin panel
# http://localhost:8000/admin/
```

### Testing & Debugging
```powershell
# Run dev server with verbose logging
python manage.py runserver 127.0.0.1:8000 --verbosity 3

# Check syntax errors
python -m py_compile smarttoll/toll/models.py

# Run admin commands
python manage.py shell
>>> from toll.models import VehicleLog
>>> VehicleLog.objects.count()
```

---

## File Quick Links

| File | Purpose | Edit When... |
|------|---------|--------------|
| `smarttoll/toll/models.py` | Data schema | Adding new entity types |
| `smarttoll/toll/api.py` | REST endpoints | Changing API response format |
| `smarttoll/toll/tasks.py` | Celery tasks & inference | **Implementing real YOLO parsing** |
| `smarttoll/toll/templates/toll/dashboard.html` | Frontend UI | Changing dashboard layout |
| `smarttoll/settings.py` | Django config | Changing database/Celery settings |
| `.env` | Environment variables | Changing model path/settings |
| `requirements.txt` | Python packages | Adding dependencies |

---

## Critical Sections

### Real Inference (Currently Stubbed)
**File**: `smarttoll/toll/tasks.py` lines 80-110

**Current Code** (Synthetic):
```python
# Creates 1-3 random detections per 30 frames
for i in range(random.randint(1, 3)):
    VehicleLog.objects.create(...)
```

**What Needs to Happen**:
```python
# Parse real OpenVINO output
output = model.infer(frame)  # Shape: (1, num_detections, 85)
# Decode: [x, y, w, h, conf, class_probs...]
# Apply NMS to filter overlapping boxes
# Create VehicleLog for each detection
```

### Dashboard Auto-Refresh
**File**: `smarttoll/toll/templates/toll/dashboard.html`

**Key Functions**:
- `fetchLiveStats()` – Called every 10 seconds
- `fetchAnalytics()` – Called every 10 seconds
- `pollUploadStatus()` – Called every 2 seconds during upload

---

## API Endpoints (Quick Reference)

```
GET  /api/stats/live/
GET  /api/stats/hourly/?date=2024-01-15
POST /api/upload/video/
GET  /api/upload/status/?id=<uuid>
GET  /api/audit/export/?date=2024-01-15
```

All require login. Test with:
```bash
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/stats/live/
```

---

## Database Relationships

```
User (Django built-in)
├── VehicleLog (multiple)
│   └── VehicleClass (per detection)
│   └── TollBooth (camera location)
├── VideoUpload (multiple uploads)
    └── Creates → VehicleLog entries

DailyAudit (Pre-aggregated)
└── Sums VehicleLog by date
```

---

## Environment Variables (.env)

```bash
# Current (Windows Local Dev)
USE_SQLITE=true
USE_EAGER_CELERY=true

# For Production
USE_SQLITE=false              # Use PostgreSQL instead
USE_EAGER_CELERY=false        # Use real Celery worker + Redis
```

---

## Troubleshooting (2-Min Fixes)

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError: No module named 'toll'" | Activate venv: `.\.venv\Scripts\activate` |
| "Connection refused at localhost:8000" | Server not running. Run: `python manage.py runserver` |
| "No data on dashboard" | Upload a video first. System starts empty. |
| "Video stuck on PROCESSING" | Check Celery is running (eager mode auto-runs tasks) |
| "Can't access /admin/" | Create superuser: `python manage.py createsuperuser` |
| "OpenVINO not found" | Check .env `OPENVINO_MODEL_XML` path is correct |

---

## Git Workflow

```powershell
# See changes
git status

# Stage changes
git add .

# Commit
git commit -m "Feature: Real inference decoding"

# View history
git log --oneline

# Create branch for refinement
git checkout -b feature/real-inference
```

---

## Performance Tips

- **Dashboard slow?** Check "Live Feed" auto-refresh interval (currently 10s)
- **Video processing slow?** Reduce frame resolution in `tasks.py` or skip frames
- **Database slow?** Check indexes exist: `python manage.py sqlsequencereset toll | python manage.py shell`
- **Memory high?** Video loading holds entire file in RAM; for large videos, implement streaming

---

## Next Refinements (Copy-Paste Ready)

### 1. Real Inference
```python
# In process_video_upload_task()
output = model.infer(frame)
# TODO: Parse output, apply NMS, create VehicleLog
```

### 2. Vehicle Tracking
```python
# In process_video_upload_task()
tracker = ByteTrack()  # Or centroid tracking
tracked_ids = tracker.update(detections)
# TODO: Filter duplicate IDs
```

### 3. PDF Export
```python
# New task
from reportlab.pdfgen import canvas
def export_audit_pdf_task(audit_id):
    # TODO: Generate PDF from DailyAudit
```

---

## Useful Django Shell Snippets

```python
from toll.models import *

# Count all detections today
from django.utils import timezone
today = timezone.now().date()
VehicleLog.objects.filter(timestamp__date=today).count()

# Revenue calculation
total_revenue = sum(
    log.vehicle_class.toll_rate 
    for log in VehicleLog.objects.filter(timestamp__date=today)
)

# Detections by class
from django.db.models import Count
VehicleLog.objects.values('vehicle_class__class_name').annotate(count=Count('id'))

# Create test data
booth = TollBooth.objects.first()
car_class = VehicleClass.objects.get(id=0)
VehicleLog.objects.create(booth=booth, vehicle_class=car_class, confidence_score=0.95)
```

---

**Last Updated**: January 2025  
**Status**: MVP Complete ✅  
**Ready for**: Refinement & Demonstration  
