from django.urls import path, include


urlpatterns = [
    path("", include("apps.products.urls")),
    path("", include("apps.facilities.urls")),
    path("warehouse/", include("apps.warehouse.urls")),
    path("", include("apps.clients.urls")),
    path("", include("apps.sales.urls")),
    path("", include("apps.staff.urls")),
]
