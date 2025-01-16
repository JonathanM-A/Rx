from django.utils.translation import gettext_lazy as _
from dj_rest_auth.views import PasswordResetConfirmView
from rest_framework.response import Response


class CustomPasswordRestConfirmView(PasswordResetConfirmView):
    def post(self, request, *args, **kwargs):
        uidb64 = kwargs.get("uidb64")
        token = kwargs.get("token")
        data = request.data.copy()

        data["uid"] = uidb64
        data["token"] = token

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Password has been reset with the new password.")},
            status=200
        )
