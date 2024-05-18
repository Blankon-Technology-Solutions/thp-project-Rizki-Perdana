from django.urls import path
from todo_api.consumers import TodoConsumer
from allauth.account.adapter import DefaultAccountAdapter

websocket_urlpatterns = [
    path("socket/todos/", TodoConsumer.as_asgi()),
]

class AccountAdapter(DefaultAccountAdapter):

  def get_login_redirect_url(self, request):
      return '/todo_api/'