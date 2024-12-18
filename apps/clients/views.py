import random
import environ
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.core.cache import cache
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from .models import Client
from .serializers import ClientSerializer


env = environ.Env()

class ClientViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def _genereate_redis_key(self, client_id):
        return f"client_update_otp:{client_id}"

    def partial_update(self, request, *args, **kwargs):
        client = self.get_object()

        otp = str(random.randint(100000, 999999))

        otp_data = {
            "client_id": str(client.id),
            "otp": otp,
            "update_data": request.data,
            "timestamp": timezone.now().isoformat()
        }

        redis_key = self._genereate_redis_key(client.id)
        cache.set(redis_key, otp_data, 300)

        if client.email:
            try:
                send_mail(
                    "OTP for Account Update",
                    f"Your OTP to update your account is: {otp}",
                    env("EMAIL_HOST_USER"),
                    [client.email],
                    fail_silently=False
                )
            except Exception as e:
                return Response(
                    {"error": _("Failed to send OTP. Please contact support.")},
                    status=500
                )

            return Response(
                {"detail": _("OTP has been sent to client's email.")},
                status=401
            )
        return Response(
            {"error": _("No email found for client")},
            status=400
        )

    @action(detail=True, methods=["post"])
    def verify_otp(self, request, pk=None):
        client_id = self.get_object().id
        input_otp = request.data.get("otp")

        redis_key = self._genereate_redis_key(client_id)
        stored_otp_data = cache.get(redis_key, None)

        if not stored_otp_data:
            return Response(
                {"error": _("No OTP request found or OTP expired.")},
                status=400
            )

        try:
            if input_otp != stored_otp_data["otp"]:
                return Response(
                    {"error": _("Invalid OTP")},
                    status=401
                )

            client = Client.objects.get(id=stored_otp_data["client_id"])
            update_data = stored_otp_data["update_data"]

            serializer = self.get_serializer(client, data=update_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            cache.delete(redis_key)

            return Response(
                {"detail": _("Client updated successfully.")},
                status=200
            )

        except Client.DoesNotExist:
            raise NotFound(_("Client not found."))

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=400
            )
