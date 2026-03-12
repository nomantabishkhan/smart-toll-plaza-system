# Smart Toll Plaza System

Real-time vehicle detection and classification system for toll plaza auditing, built as an FYP at The Islamia University of Bahawalpur.

Uses YOLOv8 to detect **8 vehicle classes** (Auto, Bus, Car, LCV, Motorcycle, Multiaxle, Tractor, Truck) from live camera feeds or uploaded video files, counts crossings, and estimates revenue.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Django 6, Django REST Framework |
| Real-time | Django Channels (WebSocket via Daphne) |
| Background tasks | Celery + SQLite broker (Redis optional) |
| AI / CV | YOLOv8 (Ultralytics), OpenCV |
| Frontend | React, Tailwind CSS, Vite |
| Database | SQLite (dev) / PostgreSQL (prod) |

## Project Layout

```
smart-toll-plaza-system/
├── backend/          Django app, API, Celery tasks, WebSocket consumers
├── frontend/         React + Tailwind dashboard (Vite)
├── models/           YOLO model artifacts (PT, ONNX, OpenVINO)
├── docs/
│   ├── diagrams/     Architecture & UML diagrams
│   ├── SRS_SmartT.docx
│   └── SDD_SmartT.docx
├── compose.yaml      Docker Compose for production
└── README.md
```

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv ../.venv
# Windows: ..\.venv\Scripts\activate
# Linux/Mac: source ../.venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python populate_vehicle_classes.py
python manage.py createsuperuser   # optional
```

Start the ASGI server (with WebSocket support):

```bash
daphne -b 127.0.0.1 -p 8000 smarttoll.asgi:application
```

Or for development (HTTP only, no WebSocket):

```bash
python manage.py runserver 127.0.0.1:8000
```

Start Celery worker (for video processing):

```bash
python -m celery -A smarttoll worker --loglevel=info
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev          # → http://localhost:5173
```

The Vite dev server proxies `/api` and `/ws` requests to the Django backend at port 8000.

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/vehicle-classes/` | List all vehicle classes with toll rates |
| GET | `/api/stats/live/` | Today's per-class counts and revenue |
| GET | `/api/stats/hourly/` | Hourly traffic breakdown |
| GET | `/api/events/recent/` | Last 50 crossing events |
| POST | `/api/upload/video/` | Upload video for background analysis |
| GET | `/api/upload/status/?id=` | Check upload processing status |
| WS | `/ws/toll/dashboard/` | Real-time detection push events |

## Vehicle Classes (YOLO Model Output)

| ID | Class | Toll Rate |
|----|-------|-----------|
| 0 | Auto | Rs.30 |
| 1 | Bus | Rs.100 |
| 2 | Car | Rs.50 |
| 3 | LCV | Rs.120 |
| 4 | Motorcycle | Rs.20 |
| 5 | Multiaxle | Rs.200 |
| 6 | Tractor | Rs.80 |
| 7 | Truck | Rs.150 |

## Access

- Dashboard: http://localhost:5173/
- Django Admin: http://localhost:8000/admin/
- API Root: http://localhost:8000/api/

