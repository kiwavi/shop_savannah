from typing import override
from django.core.serializers.base import ObjectDoesNotExist
from django.db import transaction
from django.db.models import BooleanField, Sum, Window
from django.db.models.base import ExpressionWrapper
from django.db.models.fields import DecimalField
from django.db.models.query import Case, When
from django.db.models.sql.query import F, Value
from rest_framework import serializers


from shopping.schemas import OrderDetails
from shopping.tasks import send_email
from .models import Category, Order, OrderCategory, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "quantity", "price", "product"]


class OrderCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name", read_only=True)

    class Meta:
        model = OrderCategory
        fields = ["quantity", "category", "category_name"]

    def create(self, validated_data):
        try:
            category = Category.objects.get(pk=validated_data["category"].id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {"category": "Category not found."})

        request = self.context["request"]
        customer = request.user

        # validate that the stock exists
        if validated_data["quantity"] > category.quantity:
            raise serializers.ValidationError(
                {"quantity": f"{category.name} has less stock than the chosen amount."}
            )

        # if order of that category already exists, update it; else create
        order_category, created = OrderCategory.objects.get_or_create(
            customer=customer,
            category=category,
            order=None,
            defaults={"quantity": validated_data["quantity"]},
        )

        if not created:
            # update quantity if it already exists
            order_category.quantity = validated_data["quantity"]
            order_category.save()

        return order_category


class OrderSerializer(serializers.ModelSerializer):
    details = serializers.JSONField(
        help_text=(
            "Enter order details in JSON format. Example:\n"
            "{\n"
            '  "phone_number": "+2547XXXXXXXX",\n'
            '  "address": "Bihi Towers Shop 1, Nairobi",\n'
            '  "other_details": "Open from 6a.m to 6p.m"\n'
            "}"
        ),
    )

    class Meta:
        model = Order
        fields = ["details", "amount", "created_at"]

    def validate_details(self, value):
        if value is None:
            raise serializers.ValidationError("Details field cannot be null.")

        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Details must be a JSON object, e.g. {'phone_number': '+2547...', 'address': 'Nairobi'}."
            )

        try:
            check = OrderDetails(**value)
            return check.dict()
        except Exception as e:
            raise serializers.ValidationError(f"Invalid details: {e}")

    @override
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request", None)
        if request and request.method == "POST":
            allowed = {"details"}
            fields = {k: v for k, v in fields.items() if k in allowed}

        return fields

    def create(self, validated_data):
        # handles creation of orders
        request = self.context["request"]
        customer = request.user

        with transaction.atomic():
            # lock the order categories pivot values
            order_categories = (
                OrderCategory.objects.select_for_update()
                .filter(order__isnull=True, customer=customer)
                .select_related("category")
            )

            if not len(order_categories):
                raise serializers.ValidationError(
                    f"Bad request: You have nothing in the cart"
                )

            # fetch related categories
            category_ids_to_lock = order_categories.values_list(
                "category_id", flat=True
            )

            # lock related categories
            Category.objects.select_for_update().filter(id__in=category_ids_to_lock)

            qs = (
                OrderCategory.objects.filter(
                    order__isnull=True, customer=customer)
                .select_related("category")
                .annotate(
                    order_qty=F("quantity"),
                    current_quantity=F("category__quantity"),
                    name=F("category__name"),
                    amount=ExpressionWrapper(
                        F("quantity") * F("category__price"),
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2),
                    ),
                )
                .annotate(
                    total_amount=Window(
                        expression=Sum(F("quantity") * F("category__price")),
                    ),
                    in_stock=Case(
                        When(
                            category__quantity__gte=F("quantity"),
                            then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField(),
                    ),
                )
                .values(
                    "id",
                    "order_qty",
                    "category_id",
                    "current_quantity",
                    "name",
                    "amount",
                    "total_amount",
                    "in_stock",
                )
            )

            # confirm stock presence
            for result in qs:
                if not result["in_stock"]:
                    raise serializers.ValidationError(
                        f"Bad request: {
                            result['name']} has fewer stock than the requested amount. "
                        f"Available stock: {
                            result['current_quantity']}, requested: {
                            result['order_qty']}."
                    )

            order_category_ids = [item["id"] for item in qs]

            # create order
            order = Order.objects.create(
                customer=customer,
                details=validated_data["details"],
                amount=qs[0]["total_amount"],
            )

            # update the order categories related to this order
            OrderCategory.objects.filter(
                id__in=order_category_ids).update(
                order=order)

            # decrease the amount of each category. Bulk update
            Category.objects.bulk_update(
                [
                    Category(
                        id=item["category_id"],
                        quantity=item["current_quantity"] - item["order_qty"],
                    )
                    for item in qs
                ],
                fields=["quantity"],
            )

            # send an email to the admin
            send_email.delay(order.id)

        return order
