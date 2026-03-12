"""
Data migration: populate the 8 vehicle classes that match the YOLO model output.
Class IDs correspond to the model's metadata.yaml names mapping.
"""
from django.db import migrations

VEHICLE_CLASSES = [
    (0, "Auto", 30.00),
    (1, "Bus", 100.00),
    (2, "Car", 50.00),
    (3, "LCV", 120.00),
    (4, "Motorcycle", 20.00),
    (5, "Multiaxle", 200.00),
    (6, "Tractor", 80.00),
    (7, "Truck", 150.00),
]


def populate(apps, schema_editor):
    VehicleClass = apps.get_model("toll", "VehicleClass")
    for class_id, name, rate in VEHICLE_CLASSES:
        VehicleClass.objects.update_or_create(
            id=class_id,
            defaults={"class_name": name, "toll_rate": rate, "is_active": True},
        )


def depopulate(apps, schema_editor):
    VehicleClass = apps.get_model("toll", "VehicleClass")
    VehicleClass.objects.filter(id__in=[c[0] for c in VEHICLE_CLASSES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("toll", "0002_rename_toll_vehicl_timesta_9c3fbd_idx_toll_vehicl_timesta_b7099b_idx_and_more"),
    ]

    operations = [
        migrations.RunPython(populate, depopulate),
    ]
