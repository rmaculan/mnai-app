from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/messages/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
]

wsPattern = websocket_urlpatterns
