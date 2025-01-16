from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from .models import Client, InsuranceCorporateCompany
from ..users.serializers import UserSerializer
from ..common.helpers import generate_secure_password


class InsuranceCorporateCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCorporateCompany
        fields = ["name", "is_insurance", "is_corporate"]

    def to_representation(self, instance):
        if instance.is_insurance:
            return {"name": instance.name, "type": "insurance"}
        else:
            return {"name": instance.name, "type": "corporate"}


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)
    parent_account = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), required=False
    )
    insurance_corporate_company = InsuranceCorporateCompanySerializer(required=False)

    class Meta:
        model = Client
        fields = [
            "id",
            "user",
            "password",
            "first_name",
            "last_name",
            "age",
            "gender",
            "email",
            "phone_number",
            "parent_account",
            "insurance_corporate_company",
            "is_insurance",
            "is_corporate",
            "insurance_corporate_id",
        ]

    def validate_password(self, password):
        user = self.context["request"].user

        if user.is_employee and password:
            raise serializers.ValidationError(
                _("You are not allowed to set a password.")
            )
        validate_password(password)

        return password

    def validate(self, data):
        data = super().validate(data)
        user = self.context["request"].user

        password = data.get("password", None)
        age = data.get("age", None)
        phone_number = data.get("phone_number", None)
        parent_account = data.get("parent_account", None)
        is_insurance = data.get("is_insurance", None)
        insurance_corporate_company = data.get("insurance_corporate_company", None)
        is_corporate = data.get("is_corporate", None)
        insurance_corporate_id = data.get("insurance_corporate_id", None)

        if not password:
            if user.is_anonymous:
                raise serializers.ValidationError(_("A password must be provided"))
            else:
                password = generate_secure_password()
                data["password"] = password

        if is_insurance and (is_corporate or insurance_corporate_company.is_corporate):
            raise serializers.ValidationError(
                _(
                    "A client cannot be both insurance-affiliated and corporate-affiliated."
                )
            )
        if is_insurance:
            if (
                not insurance_corporate_company.is_insurance
                or not insurance_corporate_id
            ):
                raise serializers.ValidationError(
                    _(
                        "Insurance clients must have an insurance company and an insurance ID."
                    )
                )

        if is_corporate:
            if (
                not insurance_corporate_company.is_corporate
                or not insurance_corporate_id
            ):
                raise serializers.ValidationError(
                    _(
                        "Corporate clients must have a corporate company and a corporate ID."
                    )
                )

        if not is_insurance and not is_corporate:
            if insurance_corporate_company or insurance_corporate_id:
                raise serializers.ValidationError(
                    _(
                        "Non-affiliated clients cannot have insurance or corporate details."
                    )
                )

        if age > 18 and not (phone_number):
            raise serializers(_("Phone number is required for persons over 18."))

        if age < 18:
            if not parent_account:
                raise serializers.ValidationError(
                    _("Minors must be affiliated to a parent or guardian.")
                )
            else:
                try:
                    parent = Client.objects.get(id=parent_account.id)
                except Client.DoesNotExist:
                    raise serializers.ValidationError(_("Parent account not found."))
                if parent.age < 18:
                    raise serializers.ValidationError(
                        _("Parent account must be an adult.")
                    )

        return data

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")

        email = validated_data.pop("email", None)

        user_data = {"email": email, "password": password, "is_client": True}
        serializer = UserSerializer(data=user_data, context=self.context)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        validated_data["user"] = user

        return super().create(validated_data)
