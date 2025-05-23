import json
from channels.generic.websocket import AsyncWebsocketConsumer

class JamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"jam_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✅ CONNECTED: {self.channel_name} in {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ DISCONNECTED: {self.channel_name}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"🎧 RECEIVED from {self.channel_name}: {data}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "jam_broadcast",
                "action": data.get("action"),
                "song_id": data.get("song_id"),
                "sender": data.get("sender"),
            }
        )

    async def jam_broadcast(self, event):
        print(f"📡 BROADCAST TO ROOM: {event}")
        await self.send(text_data=json.dumps(event))
