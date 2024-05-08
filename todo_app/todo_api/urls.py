from rest_framework.routers import DefaultRouter
from views import TodoViewSet

router = DefaultRouter()
router.register(r"todo_api", TodoViewSet, basename="todo_api")

urlpatterns = router.urls