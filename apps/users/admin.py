from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = (
        "id",
        "email",
    )
    search_fields = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_superuser", "is_employee", "is_client")},
        ),
        ("Important dates", {"fields": ("created_at", "modified_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_employee",
                    "is_client"
                ),
            },
        ),
    )

admin.site.register(User, UserAdmin)
