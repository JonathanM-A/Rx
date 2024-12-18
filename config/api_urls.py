from django.urls import path, include


urlpatterns = [
    path("", include("apps.products.urls")),
    path("", include("apps.users.urls")),
    path("", include("apps.facilities.urls")),
    path("", include("apps.warehouse.urls")),
    path("", include("apps.clients.urls")),
    path("", include("apps.cart.urls")),
]
