from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from .models import Staff
from .serializers import StaffSerializer
from .permissions import IsAdmin, IsManagement


class StaffViewSet(ModelViewSet):
    permission_classes = [IsAdmin | IsManagement | IsAdminUser]
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    http_method_names = [m for m in ModelViewSet.http_method_names if m != "delete"]
    filterset_fields = [
        "facility__name",
        "is_warehouse",
        "is_admin",
        "facility__region",
        "facility__city",
        "facility__country",
    ]
    search_fields = ["name"]

    def get_queryset(self):
        user = self.request.user.staff
        if user.is_management:
            queryset = Staff.objects.all().select_related("facility", "user")
        elif user.is_warehouse:
            queryset = Staff.objects.filter(is_warehouse=True).select_related("user")
        else:
            queryset = Staff.objects.filter(facility=user.facility).select_related(
                "facility", "user"
            )
        return queryset

    def create(self, request, *args, **kwargs):
        user = request.user.staff
        data = request.data.copy()

        facility = data.get("facility", None)
        is_warehouse = data.get("is_warehouse", None)
        is_management = data.get("is_management", None)

        if user.is_management:
            if not facility and not(is_management or is_warehouse):
                raise ValidationError(_("Facility is required"))
        elif user.is_warehouse:
            if facility or not is_warehouse or is_management:
                raise ValidationError(
                    _("User can only create warehouse staff")
                )
        elif not user.is_warehouse:
            data["facility"] = user.facility.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response(serializer.data, status=201)
