from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from rest_framework import permissions
from drf_rw_serializers import viewsets
from todo_api.filters import TodoFilter
from todo_api.serializers import TodoDeSerializer, TodoSerializer
from todo_api.models import Todo


class TodoViewSet(viewsets.ModelViewSet):
    is_authenticated = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filter_todo = TodoFilter
    
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    
    
    def get_serializer_class(self):
        if self.action in ['list', 'get']:
            return TodoSerializer

        return TodoDeSerializer
    
def websocket(request):
    return render(request, "websocket.html")