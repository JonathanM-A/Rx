from django.utils.translation import gettext_lazy as _
from django.db.models import F
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .models import Cart, Sale, Order
from .serializers import CartSerializer, SaleSerializer, OrderSerializer
from ..staff.permissions import IsRetail, IsAdmin
from ..users.permissions import IsClient


class CartViewSet(ModelViewSet):
    permission_classes = [IsRetail | IsClient]
    queryset = Cart.objects.none()
    serializer_class = CartSerializer
    http_method_names = [
        m for m in ModelViewSet.http_method_names if m not in ["put", "patch"]
        ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        user = self.request.user

        if user.is_employee:
            queryset = (
                Cart.objects.all().select_related("client").prefetch_related("facility_products")
            )
        else:
            queryset = (
                Cart.objects.filter(client=user.client)
                .select_related("client")
                .prefetch_related("facility_products")
            )

        return queryset


class SaleViewSet(ModelViewSet):
    permission_classes = []
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    http_method_names = ["get", "post", "delete"]

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve"]:
            permission_classes = [IsRetail | IsClient]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "staff"):
            user = user.staff
            queryset = Sale.objects.filter(facility=user.facility).prefetch_related("facility_products")
        else:
            queryset = Sale.objects.filter(client=user.client).prefetch_related("facility_products")
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        sale = self.get_object()

        if timezone.now() - sale.created_at > timezone.timedelta(weeks=1):
            return Response(
                {"detail": _("Sale cannot be reversed. Contact IT Support.")},
                status=400,
            )
        sale_products = sale.salefacilityproduct_set.all()

        for sale_product in sale_products:
            facility_product = sale_product.facility_product
            quantity = sale_product.quantity

            facility_product.quantity = F("quantity") + quantity
            facility_product.save()

        return super().destroy(request, *args, **kwargs)


class OrderViewSet(ModelViewSet):
    permission_classes = [IsClient]
    serializer_class = OrderSerializer
    queryset = Order.objects.none()
    http_method_names = [
        m for m in ModelViewSet.http_method_names if m not in ["put", "delete"]
    ]

    TERMINAL_STATUSES = ["completed", "cancelled"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_permissions(self):
        if self.action in ["create"]:
            permission_classes = [IsClient]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsClient|IsRetail]
        else:
            permission_classes = [IsRetail]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "client"):
            return Order.objects.filter(client=user.client)
        else:
            return Order.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({"detail":_("Cart is empty.")})
        return super().list(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        order = self.get_object()

        if order.status in self.TERMINAL_STATUSES:
            raise ValidationError(
                    {
                        "status":_(f"Cannot modify order in {order.status} status")
                    }
                )

        new_status = request.data.get("status", None)
        if not new_status:
            raise ValidationError(_("The 'status' field is required"))

        try:
            with transaction.atomic():
                response = super().partial_update(request, *args, **kwargs)
                order.refresh_from_db()

                if order.status == "completed":
                    sale_data = {
                        "facility": user.staff.facility.id,
                        "client": order.client.id,
                        "order": order.id,
                        "payment_method": order.payment_method,
                    }

                    serializer = SaleSerializer(
                        data=sale_data, context={"request": request}
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

                return Response(
                    {
                        "detail": _(
                            f"Order status updated to: '{order.status.title()}'"
                        ),
                        "data": response.data,
                    }, status=200
                )

        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError({
                "detail": _(f"Failed to update order: {str(e)}")
            })
