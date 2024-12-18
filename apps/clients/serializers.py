from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from .models import Client
from ..facilities.models import Facility


class ClientSerializer(serializers.ModelSerializer):
    parent_account = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), required=False, allow_null=True
    )
    # Consider ID only
    class Meta:
        model = Client
        fields = [
            "id",
            "first_name",
            "last_name",
            "age",
            "gender",
            "email",
            "phone_number",
            "parent_account",
            "is_insurance",
            "insurance_company",
            "is_corporate",
            "corporate_company",
            "insurance_corporate_id",
        ]

    def validate(self, data):
        data = super().validate(data)
        
        age = data.get("age", None)
        email = data.get("email", None)
        phone_number = data.get("phone_number", None)
        parent_account = data.get("parent_account", None)
        is_insurance = data.get("is_insurance", None)
        insurance_company = data.get("insurance_company", None)
        is_corporate = data.get("is_corporate", None)
        corporate_company = data.get("corporate_company", None)
        insurance_corporate_id = data.get("insurance_corporate_id", None)

        if is_insurance and (is_corporate or corporate_company):
            raise serializers.ValidationError(
                _("A client cannot be both insurance-affiliated and corporate-affiliated.")
            )
        if is_insurance:
            if not insurance_company or not insurance_corporate_id:
                raise serializers.ValidationError(
                    _("Insurance clients must have an insurance company and an insurance ID.")
                )

        if is_corporate:
            if not corporate_company or not insurance_corporate_id:
                raise serializers.ValidationError(
                    _("Corporate clients must have a corporate company and a corporate ID.")
                )

        if not is_insurance and not is_corporate:
            if insurance_company or corporate_company or insurance_corporate_id:
                raise serializers.ValidationError(
                    _("Non-affiliated clients cannot have insurance or corporate details.")
                )

        if age and  age > 18 and not (phone_number or email):
            raise serializers(
                _("Phone number and Email are required for persons over 18.")
            )

        if age and age < 18:
            if not parent_account:
                raise serializers.ValidationError(
                    _("Minors must be affiliated to a parent or guardian.")
                )
            else:
                try:
                    parent = Client.objects.get(id=parent_account.id)
                    data["email"] = parent.email
                except Client.DoesNotExist:
                    raise NotFound(_("Parent account does not exist."))

        if not parent_account:
            email = data.get("email", None)
            if email:
                if Client.objects.filter(email=email).exists():
                    raise serializers.ValidationError(
                        _("An account already exists with this email address")
                    )

        return data
