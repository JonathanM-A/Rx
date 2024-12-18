from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db import models
from django.db.models.signals import pre_save
from django.core.validators import MinLengthValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from ..common.validators import phone_validator
from ..common.models import BaseModel


class Client(BaseModel):
    GENDER_CHOICES = [("male", "Male"), ("female", "Female"), ("other", "Other")]

    INSURANCE_COMPANY = [
        ("acacia", "Acacia Health Insurance"),
        ("apex", "Apex Health Insurance"),
        ("glico_health", "Glico Health Insurane"),
        ("glico_tpa", "Glico TPA"),
    ]

    CORPORATE_COMPANY = [
        ("vivo", "Vivo Energy Limited"),
        ("mtn", "MTN Ghana"),
        ("stanbic_bank", "Stanbic Bank Ghana"),
    ]

    first_name = models.CharField(null=False, blank=False)
    last_name = models.CharField(null=False, blank=False)
    age = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(0)])
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(
        unique=False,
        null=True,
        blank=False,
        validators=[phone_validator, MinLengthValidator(10)],
    )
    gender = models.CharField(choices=GENDER_CHOICES, null=False, blank=False)
    parent_account = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=False
    )
    is_insurance = models.BooleanField(default=False, null=False, blank=False)
    insurance_company = models.CharField(
        choices=INSURANCE_COMPANY, null=True, blank=False
    )
    is_corporate = models.BooleanField(default=False, null=False, blank=False)
    corporate_company = models.CharField(
        choices=CORPORATE_COMPANY, null=True, blank=False
    )
    insurance_corporate_id = models.CharField(null=True, blank=False)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return self.name

    def clean(self) -> None:
        super().clean()
        # Check mutual exclusivity of insurance and corporate status
        if self.is_insurance and (self.is_corporate or self.corporate_company):
            raise ValidationError(
                _(
                    "A client cannot be both insurance-affiliated and corporate-affiliated."
                )
            )

        # Validation for insurance clients
        if self.is_insurance:
            if not self.insurance_company or not self.insurance_corporate_id:
                raise ValidationError(
                    _(
                        "Insurance clients must have an insurance company and an insurance ID."
                    )
                )

        # Validation for corporate clients
        if self.is_corporate:
            if not self.corporate_company or not self.insurance_corporate_id:
                raise ValidationError(
                    _(
                        "Corporate clients must have a corporate company and a corporate ID."
                    )
                )

        # Validation for non-affiliated clients
        if not self.is_insurance and not self.is_corporate:
            if (
                self.insurance_company
                or self.corporate_company
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

        # Validation for phone numbers and email
        if self.age < 18:
            if not self.parent_account:
                raise ValidationError(
                    _("Minors must be affiliated to a parent or guardian.")
                )
            if self.parent_account:
                try:
                    parent = Client.objects.get(id=self.parent_account.id)
                    self.email = parent.email
                except Client.DoesNotExist:
                    raise ValidationError(_("Parent account does not exist."))
            else:
                raise ValidationError(
                    _("Minors must be linked to a parent account")
                )

        if not self.parent_account:
            email = self.email
            if Client.objects.filter(email=email).exists():
                raise ValidationError(
                    _("An account already exists with this email address")
                )

    def save(self, *args, **kwargs):
        if not self.slug:
            string = str(self.id[:8])
            self.slug = slugify(string)
        super().save(*args, **kwargs)

@receiver(pre_save, sender=Client)
def client_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        base_slug = slugify(str(instance.id)[:8])
        slug = base_slug
        num = 1
        while Client.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{num}"
            num += 1
        instance.slug = slug