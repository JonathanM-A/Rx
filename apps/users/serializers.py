from rest_framework import serializers
from .models import User
from ..facilities.models import Facility
from ..common.serializers import BaseModelSerializer


class UserSerializer(BaseModelSerializer):
    password = serializers.CharField(write_only=True)
    facility = serializers.PrimaryKeyRelatedField(queryset=Facility.objects.all(), required=False)

    class Meta:
        model = User
        fields = [
            "name",
            "email",
            "password",
            "facility",
            "is_warehouse",
            "is_staff",
            "is_admin",
            "is_management",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.facility:
            data["facility"] = str(instance.facility)
        else:
            data["facility"] = None
        return data
