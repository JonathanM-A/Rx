import random
import environ
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.core.cache import cache
from django.core.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Client, InsuranceCorporateCompany
from ..users.permissions import IsClient
from ..staff.permissions import IsAdmin, IsRetail
from ..common.helpers import generate_redis_key
from .serializers import (
    ClientSerializer,
    InsuranceCorporateCompanySerializer,
)
env = environ.Env()


class InsuranceCorporateCompanyView(ListCreateAPIView):
    permission_classes = []
    serializer_class = InsuranceCorporateCompanySerializer
    queryset = InsuranceCorporateCompany.objects.all()

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [IsRetail]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class ClientViewSet(ModelViewSet):
    permission_classes = [IsRetail | IsClient]
    queryset = Client.objects.all().order_by("-first_name")
    serializer_class = ClientSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["first_name", "last_name", "phone_number", "user__email"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        elif self.action == "partial_update":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsRetail]
        return [permission() for permission in permission_classes]

    def partial_update(self, request, *args, **kwargs):
        if request.data["password"]:
            raise PermissionDenied("Password cannot be altered from this view.")
        if request.user.is_client:
            return self.partial_update(request, *args, **kwargs)
        
        client = self.get_object()

        otp = str(random.randint(100000, 999999))

        otp_data = {
            "client_id": str(client.id),
            "otp": otp,
            "update_data": request.data,
            "timestamp": timezone.now().isoformat(),
        }

        redis_key = generate_redis_key(client.id)
        cache.set(redis_key, otp_data, 300)

        if client.user.email:
            try:
                send_mail(
                    _("OTP for Account Update"),
                    _(f"Your OTP to update your account is: {otp}"),
                    env("EMAIL_HOST_USER"),
                    [client.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                return Response(
                    {"error": _("Failed to send OTP. Please contact support.")},
                    status=500,
                )

            return Response(
                {"detail": _("OTP has been sent to client's email.")}, status=401
            )
        return Response({"error": _("No email found for client")}, status=400)

    @action(detail=True, methods=["post"])
    def verify_otp(self, request, pk=None):
        client = self.get_object()
        input_otp = request.data.get("otp")

        redis_key = generate_redis_key(client.id)
        stored_otp_data = cache.get(redis_key, None)

        if not stored_otp_data:
            return Response(
                {"error": _("No OTP request found or OTP expired.")}, status=400
            )

        try:
            if input_otp != stored_otp_data["otp"]:
                return Response({"error": _("Invalid OTP")}, status=401)

            client = Client.objects.get(id=stored_otp_data["client_id"])
            update_data = stored_otp_data["update_data"]

            serializer = self.get_serializer(client, data=update_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            cache.delete(redis_key)

            return Response({"detail": _("Client updated successfully.")}, status=200)

        except Client.DoesNotExist:
            return Response({"error": _("Client not found.")}, status=404)

        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

