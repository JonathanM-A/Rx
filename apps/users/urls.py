from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import UserViewSet, LogoutView

router = DefaultRouter()
router.register(r"users", UserViewSet)

# app_name = "users"
urlpatterns = [
    # path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
]
