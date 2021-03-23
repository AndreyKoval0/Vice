from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path('ws/messages/', consumers.ChatConsumer),
    re_path('ws/files/', consumers.ChatFileConsumer),
]