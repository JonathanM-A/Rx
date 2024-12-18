from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from .models import User
from .serializers import UserSerializer
from .permissions import IsManager, IsAdminUser


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.none()

    filterset_fields = [
        "facility__name",
        "facility__region",
        "facility__country",
        "facility__city",
    ]
    search_fields = ["name"]

    def get_permissions(self):
        if self.action == "change_password":
            permission_classes = [IsAuthenticated]
        if self.action in ["list", "retrieve", "create"]:
            permission_classes = [IsAdminUser | IsManager]
        else:
            permission_classes = [IsManager]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_management:
            return User.objects.select_related("facility")
        else:
            return User.objects.filter(facility=user.facility).select_related(
                "facility"
            )

    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        
        user = request.user
        old_password = request.data.get("old password")
        new_password1 = request.data.get("new password")
        new_password2 = request.data.get("confirm password")

        if not user.check_password(old_password):
            return Response({"detail":_("Incorrect password")}, status=400)

        if old_password == new_password1:
            return Response(
               { "detail":_("New password cannot be the same as old password")}, status=400
            )

        if new_password1 == new_password2:
            user.set_password(new_password1)
            user.save()
            return Response({"detail":_("Password changed")}, status=200)
        return Response("Passwords do not match", status=400)


class LogoutView(TokenBlacklistView):
    def post(self, request, *args, **kwargs):
        auth_token = request.headers.get("Authorization")
        if not auth_token:
            return Response({"detail":_("Token not provided")}, status=400)
        refresh_token = (
            auth_token.split(" ")[1] if auth_token.startswith("Bearer ") else None
        )
        if refresh_token:
            try:
                token = OutstandingToken.objects.get(token=refresh_token)
                BlacklistedToken.objects.create(token=token)
                return Response({"detail":_("Log out successful")}, status=200)
            except OutstandingToken.DoesNotExist:
                return Response({"detail":_("Invalid token")}, status=404)

        return Response(_("Not Authorised"), status=401)
