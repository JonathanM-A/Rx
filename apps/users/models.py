from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ..common.models import BaseModel


class UserManager(BaseUserManager):

    def create_user(
        self, email, password 
    ):
        if not email:
            raise ValueError("Users must have an email")
        if not password:
            raise ValueError("Users must have a password")

        try:
            validate_password(password)
        except ValidationError as e:
            raise ValueError(f"Invalid password: {e.message}")

        user = self.model(
            email=self.normalize_email(email),
        )
        validate_password(password=password)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, name, password):
        if not email:
            raise ValueError("Users must have an email")
        if not password:
            raise ValueError("Users must have a password")

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.is_staff, user.is_superuser = True, True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    email = models.EmailField(unique=True, null=False, blank=False)
    is_employee = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["is_employee", "is_client"]
    class Meta:
        ordering = ["email"]

    def __str__(self) -> str:
        return f"{self.email}"
    