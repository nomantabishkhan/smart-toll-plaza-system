"""
WebSocket consumer for real-time toll plaza updates.
Pushes live vehicle detection counts and crossing events to the frontend.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TollDashboardConsumer(AsyncWebsocketConsumer):
    """
    Clients connect to ws://.../ws/toll/dashboard/
    They receive real-time updates whenever a vehicle detection is logged.
    """

    GROUP_NAME = "toll_dashboard"

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Clients don't send data; this is a push-only channel.
        pass

    # ---- custom event handlers (sent from backend via channel_layer) ----

    async def vehicle_detected(self, event):
        """Fired each time a new VehicleLog is created."""
        await self.send(text_data=json.dumps({
            "type": "vehicle_detected",
            "data": event["data"],
        }))

    async def stats_update(self, event):
        """Periodic or on-demand summary of today's counts."""
        await self.send(text_data=json.dumps({
            "type": "stats_update",
            "data": event["data"],
        }))
