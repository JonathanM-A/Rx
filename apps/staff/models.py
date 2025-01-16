from django.db import models
from ..users.models import User
from ..common.models import BaseModel
from ..facilities.models import Facility


class Staff(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="staff", 
        limit_choices_to={"is_employee": True}
        )
    name = models.CharField(blank=False)
    facility = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, related_name="staff", null=True
        )
    is_warehouse = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_management = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

