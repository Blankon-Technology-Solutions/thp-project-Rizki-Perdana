from pyexpat import model
from drf_model_serializer import serializers
from models import Todo

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = '__all__'


class TodoDeSerializer(serializers.ModelSerializer):
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
    
    def iterate(self, payload):
        payload['user'] = self.context['request'].user
        return super().create(payload)