import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TripConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.trip_id = self.scope["url_route"]["kwargs"]["trip_id"]
        self.group_name = f"trip_{self.trip_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print("✅ WebSocket connected for trip", self.trip_id)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_location(self, event):
        await self.send(text_data=json.dumps({
            "lat": event["lat"],
            "lon": event["lon"]
        }))
