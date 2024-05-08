from pyexpat import model
from django_filters import FilterSet, CharFilter, BooleanFilter
from models import Todo


class TodoFilter(FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains')
    description = CharFilter(field_name='description', lookup_expr='icontains')
    is_completed = BooleanFilter(field_name='is_completed')
    
    class Meta:
        model = Todo
        fields = ['title', 'description', 'is_completed']