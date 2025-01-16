from django.utils.translation import gettext_lazy as _
from django.db import transaction
from rest_framework import serializers
from .models import Staff
from ..users.models import User
from ..users.serializers import UserSerializer
from ..facilities.models import Facility
from ..common.helpers import generate_secure_password


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    email = serializers.EmailField(write_only=True)
    facility = serializers.PrimaryKeyRelatedField(
        queryset=Facility.objects.filter(is_active=True),
        allow_null = True,
        write_only=True,
    )
    facility_name = serializers.StringRelatedField(read_only=True, source="facility")

    class Meta:
        model = Staff
        fields = [
            "id",
            "user",
            "email",
            "name",
            "facility_name",
            "facility",
            "is_warehouse",
            "is_admin",
            "is_management"
        ]

    def validate(self, data):
        data = super().validate(data)

        is_warehouse = data.get("is_warehouse", None)
        is_management = data.get("is_management", None)
        facility = data.get("facility", None)

        if not (is_warehouse or is_management) and not facility:
            raise serializers.ValidationError(_("Facility is required"))

        elif (is_warehouse or is_management) and facility:
            raise serializers.ValidationError(_("Facility is not allowed."))

        return data

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.pop("email", None)
        password = generate_secure_password()

        user_data = {
            "email":email,
            "is_employee":True,
            "password": password
            }
        
        serializer = UserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        validated_data["user"] = user

        return super().create(validated_data)
