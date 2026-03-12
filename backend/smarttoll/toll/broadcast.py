"""
Utility to push real-time events to WebSocket clients.
Call these functions from tasks.py or views.py after creating a VehicleLog.
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone


def broadcast_vehicle_detected(vehicle_class_name: str, confidence: float, booth_name: str = ""):
    """Push a single detection event to all connected dashboard clients."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        "toll_dashboard",
        {
            "type": "vehicle_detected",
            "data": {
                "vehicle_class": vehicle_class_name,
                "confidence": round(confidence, 3),
                "booth": booth_name,
                "timestamp": timezone.now().isoformat(),
            },
        },
    )


def broadcast_stats_update(stats: dict):
    """Push an aggregated stats snapshot to all connected dashboard clients."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        "toll_dashboard",
        {
            "type": "stats_update",
            "data": stats,
        },
    )
