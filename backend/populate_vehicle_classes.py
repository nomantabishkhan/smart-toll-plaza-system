"""
Populate VehicleClass table with the 8 custom classes
Run this script: python populate_vehicle_classes.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarttoll.settings')
django.setup()

from smarttoll.toll.models import VehicleClass

# Your 8 classes in exact YOLO training order
# Format: (class_id, class_name, toll_rate)
VEHICLE_CLASSES = [
    (0, 'Car', 50.00),
    (1, 'Truck', 150.00),
    (2, 'Bus', 100.00),
    (3, 'Motorcycle', 20.00),
    (4, 'Auto', 30.00),
    (5, 'Tractor', 80.00),
    (6, 'LCV', 120.00),
    (7, 'Multiaxle', 200.00),
]

def populate_classes():
    print("🚗 Populating Vehicle Classes...")
    print("-" * 50)
    
    for class_id, name, rate in VEHICLE_CLASSES:
        obj, created = VehicleClass.objects.update_or_create(
            id=class_id,
            defaults={
                'class_name': name,
                'toll_rate': rate,
                'is_active': True
            }
        )
        status = "✅ Created" if created else "♻️  Updated"
        print(f"{status} | ID: {class_id} | {name:15} | ₹{rate:7.2f}")
    
    print("-" * 50)
    print(f"✅ Successfully populated {len(VEHICLE_CLASSES)} vehicle classes!")
    print(f"📊 Total classes in database: {VehicleClass.objects.count()}")

if __name__ == '__main__':
    populate_classes()
