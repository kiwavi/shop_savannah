from django.core.serializers.base import ObjectDoesNotExist
from rest_framework import serializers
from .models import Category, OrderCategory, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name","description","quantity","price","product"]

class OrderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCategory
        fields = ["quantity", "category"]

    def create(self, validated_data):
        try:
            category = Category.objects.get(pk=validated_data["category"].id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"category": "Category not found."})

        request = self.context["request"]
        customer = request.user

        # validate that the stock exists
        if validated_data["quantity"] > category.quantity:
            raise serializers.ValidationError({
                "quantity": f"{category.name} has less stock than the chosen amount."
            })

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
