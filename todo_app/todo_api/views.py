from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from drf_rw_serializers import viewsets
from filters import TodoFilter
from serializers import TodoDeSerializer, TodoSerializer
from models import Todo


class TodoViewSet(viewsets.ModelViewSet):
    is_authenticated = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filter_todo = TodoFilter
    
    
    def queryset(self):
        return Todo.objects.filter(user=self.request.user)
    
    
    def serializer(self):
        if self.action in ['list', 'get']:
            return TodoSerializer

        return TodoDeSerializer