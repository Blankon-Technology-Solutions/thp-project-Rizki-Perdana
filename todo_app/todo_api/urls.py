from django.urls import path
from rest_framework.routers import DefaultRouter
from todo_api.views import TodoViewSet, websocket

router = DefaultRouter()
router.register(r"todo_api", TodoViewSet, basename="todo_api")

urlpatterns = router.urls
urlpatterns += [
    path('websocket', websocket, name="websocket")
]