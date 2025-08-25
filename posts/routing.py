from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/like_comment/$", consumers.LikeCommentConsumer.as_asgi()),
]
