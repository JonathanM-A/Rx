from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import User
from ..common.serializers import BaseModelSerializer


class UserSerializer(BaseModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id"
            "email",
            "password",
            "is_staff",
            "is_employee",
            "is_client",
        ]

    def validate(self, data):
        data = super().validate(data)

        is_staff = data.get("is_staff", None)
        is_employee = data.get("is_employee", None)
        is_client = data.get("is_client", None)

        if (is_staff or is_employee) and is_client:
            raise serializers.ValidationError(
                {"non_field_error": _("User cannot be both staff and employee")}
            )

        if not is_employee and not is_client:
            raise serializers.ValidationError(
                {"non_field_eror": _("User must be either staff or client")}
                )

        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
