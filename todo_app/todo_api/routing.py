from django.urls import path
from todo_api.consumers import TodoConsumer

websocket_urlpatterns = [
    path("socket/todos/", TodoConsumer.as_asgi()),
]