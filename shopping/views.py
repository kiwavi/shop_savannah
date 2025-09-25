from typing import override
from django.shortcuts import render
from django.http import HttpResponse

from shopping.models import Category, OrderCategory, Product
from shopping.serializers import CategorySerializer, OrderCategorySerializer, ProductSerializer
from rest_framework import viewsets, permissions
# Create your views here.

class IsSuperAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # GET, HEAD, OPTIONS
        return request.user and request.user.is_superuser

def index(request):
    return HttpResponse("Hello World")

class ProductsViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated,IsSuperAdminOrReadOnly]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated,IsSuperAdminOrReadOnly]

class OrderCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = OrderCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       return OrderCategory.objects.filter(customer=self.request.user)
