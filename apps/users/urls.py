from django.urls import path
from .views import CustomPasswordRestConfirmView


urlpatterns = [
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        CustomPasswordRestConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]