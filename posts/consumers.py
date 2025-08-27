import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import database_sync_to_async
from models import Post

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
            post_id = data["post_id"]
            post = await database_sync_to_async(Post.objects.get)(id=post_id)
            # foydalanuvchi allaqachon like qilmaganini tekshirish
            await database_sync_to_async(post.likes.add)(self.scope["user"])
            like_count = await database_sync_to_async(lambda: post.likes.count())()

            # barcha clientlarga yuborish
            await self.channel_layer.group_send(
                "post_updates",
                {
                    "type": "send_like",
                    "post_id": post_id,
                    "like_count": like_count
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
            "post_id": event["post_id"],
            "like_count": event["like_count"]
    }))

    async def send_comment(self, event):
        await self.send(text_data=json.dumps({
            "type": "comment",
            "comment": event["comment"],
            "post_id": event["post_id"]
        }))
