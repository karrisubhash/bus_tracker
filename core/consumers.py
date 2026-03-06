from channels.generic.websocket import AsyncWebsocketConsumer
import json

class BusLocationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            "bus_locations",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "bus_locations",
            self.channel_name
        )

    async def bus_location(self, event):
        await self.send(text_data=json.dumps(event["data"]))
