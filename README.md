# Smart Toll Plaza Audit System

Django-based FYP project for toll plaza auditing with vehicle detection, upload processing, dashboard analytics, and daily audit reporting.

## Tech Stack

- Python + Django + Django REST Framework
- Celery for background processing
- SQLite (default) / PostgreSQL (optional)
- YOLO/OpenVINO model artifacts included in repository folders

## Project Layout

- `backend/` – Django app, API, templates, and business logic
- `pt/`, `ONNx file/`, `openvino file/` – model files and metadata
- `compose.yaml`, `Dockerfile` – container setup files

## Quick Start (Windows)

1. Open PowerShell and go to backend:

```powershell
cd "d:\pc data\projects\fyp smart toll plaza audit system\backend"
```

2. Create and activate virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

3. Run migrations and seed classes:

```powershell
python manage.py migrate
python manage.py shell < populate_classes.py
```

4. (Optional) Create admin user:

```powershell
python manage.py createsuperuser
```

5. Start services:

```powershell
# terminal 1
python -m celery -A smarttoll worker --loglevel=info

# terminal 2
python manage.py runserver 127.0.0.1:8000
```

## Access

- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Notes

- Copy `.env.example` to `.env` in `backend/` for local configuration.
- `.env`, runtime logs, and local DB artifacts are ignored from Git.
