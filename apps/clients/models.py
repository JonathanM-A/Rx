from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from django.core.exceptions import ValidationError
from ..common.validators import phone_validator
from ..common.models import BaseModel
from ..users.models import User


class InsuranceCorporateCompany(BaseModel):
    name = models.CharField(unique=True, blank=False)
    is_insurance = models.BooleanField(blank=False)
    is_corporate = models.BooleanField(blank=False)

    def __str__(self):
        return self.name


class Client(BaseModel):
    GENDER_CHOICES = [("male", "Male"), ("female", "Female"), ("other", "Other")]

    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, related_name="client", 
        limit_choices_to={"is_client": True}, null=True
    )
    first_name = models.CharField(null=False, blank=False)
    last_name = models.CharField(null=False, blank=False)
    age = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(0)])
    phone_number = models.CharField(
        null=True,
        blank=False,
        validators=[phone_validator, MinLengthValidator(10)],
    )
    gender = models.CharField(choices=GENDER_CHOICES, null=False, blank=False)
    parent_account = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=False
    )
    insurance_corporate_company = models.ForeignKey(
        InsuranceCorporateCompany, on_delete=models.SET_NULL, 
        null=True, blank=False
    )
    is_insurance = models.BooleanField(default=False, null=False, blank=False)
    is_corporate = models.BooleanField(default=False, null=False, blank=False)
    insurance_corporate_id = models.CharField(null=True, blank=False)


    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.name

    def clean(self) -> None:
        super().clean()

        if self.is_insurance and (self.is_corporate or self.insurance_corporate_company.is_corporate):
            raise ValidationError(
                _(
                    "A client cannot be both insurance-affiliated and corporate-affiliated."
                )
            )
        if self.is_insurance:
            if not self.insurance_corporate_company.is_insurance or not self.insurance_corporate_id:
                raise ValidationError(
                    _(
                        "Insurance clients must have an insurance company and an insurance ID."
                    )
                )
        if self.is_corporate:
            if not self.insurance_corporate_company.is_corporate or not self.insurance_corporate_id:
                raise ValidationError(
                    _(
                        "Corporate clients must have a corporate company and a corporate ID."
                    )
                )
        if not self.is_insurance and not self.is_corporate:
            if (
                self.insurance_corporate_company
                or self.insurance_corporate_id
            ):
                raise ValidationError(
                    _(
                        "Non-affiliated clients cannot have insurance or corporate details."
                    )
                )
        if self.age > 18 and not (self.phone_number or self.email):
            raise ValidationError(
                _("Phone number and Email are required for persons over 18.")
            )

        if self.age < 18:
            if not self.parent_account:
                raise ValidationError(
                    _("Minors must be affiliated to a parent or guardian.")
                )
            else:
                try:
                    parent = Client.objects.get(id=self.parent_account.id)
                except Client.DoesNotExist:
                    raise ValidationError(_("Parent account does not exist."))
                if parent.age < 18:
                    raise ValidationError(_("Parent account must be an adult."))
                
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
