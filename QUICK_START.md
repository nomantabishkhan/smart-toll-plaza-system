# Quick Start Guide - Smart Toll Plaza Audit System

## Start the Application

Run this command in PowerShell:

```powershell
cd "d:\pc data\projects\fyp smart toll plaza audit system\backend"

# Start both services in background
$backend = "d:\pc data\projects\fyp smart toll plaza audit system\backend"

# Start Celery Worker
Start-Process -FilePath python -ArgumentList @('-m','celery','-A','smarttoll','worker','--loglevel=info') -WorkingDirectory $backend -WindowStyle Minimized

# Wait 2 seconds
Start-Sleep -Seconds 2

# Start Django Server
Start-Process -FilePath python -ArgumentList @('manage.py','runserver','127.0.0.1:8000') -WorkingDirectory $backend -WindowStyle Minimized

# Wait for startup
Start-Sleep -Seconds 3

# Open browser
Start-Process "http://127.0.0.1:8000"
```

## Access

- **Dashboard:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
  - Username: `admin`
  - Password: `Admin@12345`

## Stop the Application

```powershell
$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'manage.py runserver|celery -A smarttoll worker' }
$procs | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

## Features

✅ Upload videos for vehicle detection  
✅ Real-time dashboard with traffic stats  
✅ 8 vehicle classes detected  
✅ Daily audit reports  
✅ Admin panel for configuration  

## Current Status

- **Mode:** DEMO (simulated detections - PyTorch unavailable)
- **Database:** SQLite with all vehicle classes populated
- **Processing:** Async via Celery worker
- **CSRF:** Fixed in dashboard upload

## Troubleshooting

If upload fails:
1. Check both services are running
2. Open browser console (F12) for errors
3. Check logs: `backend/*.log` files

If "stuck on uploading":
1. Verify Celery worker is running
2. Check `backend/celery.run.err.log` for errors
3. Restart both services
