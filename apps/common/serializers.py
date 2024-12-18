from rest_framework import serializers
from .models import BaseModel


class BaseModelSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    modified_at = serializers.DateTimeField(read_only=True)
    is_active = serializers.DateTimeField(read_only=True)

    class Meta:
        model = BaseModel
        fields = ["id", "created_at", "modified_at", "is_active"]
