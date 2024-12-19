from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ..common.models import BaseModel
from ..facilities.models import Facility


class UserManager(BaseUserManager):

    def create_user(
        self, email, name, password, facility, is_warehouse=False, is_management=False
    ):
        if not email:
            raise ValueError("Users must have an email")
        if not name:
            raise ValueError("Users must have a first and last name")
        if not password:
            raise ValueError("Users must have a password")
        if not facility and not (is_warehouse or is_management):
            raise ValueError("User must be linked to a facility")

        try:
            validate_password(password)
        except ValidationError as e:
            raise ValueError(f"Invalid password: {e.message}")

        facility_instance = None

        if facility:
            facility_instance = Facility.objects.filter(id=facility).first()
            if not facility_instance:
                raise ValueError(f"Facility with id {facility} does not exist.")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            facility=facility_instance,
            is_warehouse=is_warehouse,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, name, password):
        if not email:
            raise ValueError("Users must have an email")
        if not name:
            raise ValueError("Users must have a first and last name")
        if not password:
            raise ValueError("Users must have a password")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )
        user.set_password(password)
        user.is_staff, user.is_admin, user.is_warehouse, user.is_management, user.is_superuser = True, True, True, True, True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    email = models.EmailField(unique=True, null=False, blank=False)
    name = models.CharField(null=False, blank=False)
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, null=True, related_name="staff", blank=True
    )
    is_warehouse = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_management = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name}"
