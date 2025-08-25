import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LikeCommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("realtime", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("realtime", self.channel_name)

    async def receive(self, text_data):
        # frontenddan kelgan habar
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "like":
            await self.channel_layer.group_send(
                "realtime",
                {
                    "type": "send_like",
                    "like_count": data["like_count"],
                    "post_id": data["post_id"],
                }
            )
        elif message_type == "comment":
            await self.channel_layer.group_send(
                "realtime",
                {
                    "type": "send_comment",
                    "comment": data["comment"],
                    "post_id": data["post_id"],
                }
            )

    async def send_like(self, event):
        await self.send(text_data=json.dumps({
            "type": "like",
            "like_count": event["like_count"],
            "post_id": event["post_id"]
        }))

    async def send_comment(self, event):
        await self.send(text_data=json.dumps({
            "type": "comment",
            "comment": event["comment"],
            "post_id": event["post_id"]
        }))
