from rest_framework import serializers
from drf_model_serializer import serializers as model_serializers
from hashid_field.rest import HashidSerializerCharField
from todo_api.models import Todo

class TodoSerializer(model_serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(pk_field=HashidSerializerCharField(source_field='todo_api.Todo.id'), read_only=True)
    class Meta:
        model = Todo
        fields = '__all__'


class TodoDeSerializer(model_serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(pk_field=HashidSerializerCharField(source_field='todo_api.Todo.id'), read_only=True)
    class Meta:
        model = Todo
        fields = [
            "id",
            "title",
            "description",
            "is_completed",
            "created_at",
            "updated_at",
        ]
    
    def create(self, payload):
        payload['user'] = self.context['request'].user
        return super().create(payload)
