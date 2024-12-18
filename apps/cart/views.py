from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import ValidationError, NotFound
from .models import Sale, SaleProduct
from .serializers import (
    SaleSerializer,
)
from ..clients.models import Client
from ..facilities.models import FacilityProduct
from .helpers import generate_redis_key


class CartView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    lookup_field = "slug"


    def post(self, request, pk=None):
        try:
            client = self.get_object()
        except Http404:
            return NotFound(_("Client not found."))

        products = request.data.get("products", None)
        user = request.user

        if not isinstance(products, list):
            raise ValidationError(_("A valid list of products must be provided."))

        for product in products:
            product_id = product.get("product", None)
            quantity = product.get("quantity", None)

            try:
                product = FacilityProduct.objects.get(
                    product=product_id, facility=user.facility
                )
            except FacilityProduct.DoesNotExist:
                raise NotFound(_("Product is not available in this facility."))

            if product.quantity < quantity:
                raise ValidationError(_("Insufficient quantity."))

        cart_data = {
            "client_id": str(client.id),
            "products": products,
        }

        redis_key = generate_redis_key(client.id)
        cache.set(redis_key, cart_data, 604800)  # 5 day timeout

        return Response({"message": _("Items saved to cart.")}, status=201)

    def get(self, request, pk=None):
        try:
            client = self.get_object()
        except Http404:
            raise NotFound(_("Client not found."))

        redis_key = generate_redis_key(client.id)
        cart = cache.get(redis_key, None)

        if not cart:
            return Response({"message": "Empty Cart"}, status=200)
        else:
            return Response({"products": cart["products"]}, status=200)


class SaleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SaleSerializer
    queryset = Sale.objects.none()
    http_method_names = [
        m for m in ModelViewSet.http_method_names if m not in ["put", "patch", "post"]
    ]
    filterset_fields = ["client", "created_at"]

    def get_queryset(self):
        user_facility = self.request.user.facility

        queryset = (Sale.objects.filter(facility=user_facility)
        .select_related("client")
        .prefetch_related("saleproduct_set__facility_product__product"))
        
        return queryset

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = {"request": self.request}
        return super().get_serializer(*args, **kwargs)


class MakeSaleView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()

    @transaction.atomic()
    def post(self, request, pk=None):
        user = request.user

        try:
            client = self.get_object()
        except Http404:
            return NotFound(_("Client not found."))

        products = request.data.get("products", None)
        payment_method = request.data.get("payment_method", None)

        if not isinstance(products, list):
            raise ValidationError(_("A valid list of products must be provided."))

        if not payment_method:
            raise ValidationError(_("A valid payment method must be provided"))

        sale_instance = Sale.objects.create(
            client=client,
            facility=user.facility,
            payment_method=payment_method,
            created_by=user,
        )

        for product in products:
            product_id = product.get("product", None)
            quantity = product.get("quantity", None)

            try:
                facility_product = FacilityProduct.objects.get(
                    product=product_id, facility=user.facility
                )
            except FacilityProduct.DoesNotExist:
                raise NotFound(_("Product is not available in this facility."))

            if facility_product.quantity < quantity:
                raise ValidationError(_("Insufficient quantity"))

            SaleProduct.objects.create(
                sale=sale_instance, facility_product=facility_product, quantity=quantity
            )

            facility_product.quantity = F("quantity") - quantity
            facility_product.save()

        sale = (
            Sale.objects.filter(id=sale_instance.id)
            .select_related("client")
            .prefetch_related("facility_products")
        )
        serializer = SaleSerializer(sale, many=True)
        
        redis_key = generate_redis_key(client.id)
        cache.delete(redis_key)

        return Response({"sale": serializer.data}, status=201)


class ClientSaleHistory(GenericAPIView):
    queryset = Client.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        try:
            client = self.get_object()
        except Http404:
            raise NotFound(_("Client not found."))

        sale_history = (
            Sale.objects.filter(client=client.id)
            .select_related("client")
            .prefetch_related("facility_products")
        )
        serializer = SaleSerializer(sale_history, many=True)

        return Response({"sale_history": serializer.data}, status=200)
