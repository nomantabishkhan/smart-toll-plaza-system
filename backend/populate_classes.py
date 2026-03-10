from smarttoll.toll.models import VehicleClass

# Create 8 vehicle classes matching your model
classes = [
    (0, "Car", 100),
    (1, "Bus", 300),
    (2, "Truck", 500),
    (3, "Motorbike", 50),
    (4, "Van", 200),
    (5, "Taxi", 150),
    (6, "Heavy Truck", 800),
    (7, "Other", 100),
]

for class_id, name, rate in classes:
    obj, created = VehicleClass.objects.get_or_create(
        id=class_id,
        defaults={"class_name": name, "toll_rate": rate}
    )
    status = "Created" if created else "Exists"
    print(f"{status}: {name} (ID={class_id}, Rate={rate})")

print("\nVehicle classes populated successfully!")
