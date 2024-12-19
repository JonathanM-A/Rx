from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = (
        "id",
        "email",
        "name",
        "facility",
        "is_warehouse",
        "is_admin",
        "is_management",
        "is_active",
        "created_at",
        "modified_at",
    )
    list_filter = ("is_admin", "is_warehouse", "is_management", "is_active")
    search_fields = ("email", "name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name", "facility")}),
        (
            "Permissions",
            {"fields": ("is_admin", "is_warehouse", "is_management", "is_active")},
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
                    "name",
                    "facility",
                    "password1",
                    "password2",
                    "is_admin",
                    "is_warehouse",
                    "is_management",
                    "is_warehouse",
                ),
            },
        ),
    )

admin.site.register(User, UserAdmin)
