from django.shortcuts import render
from django.http import HttpResponse

from shopping.models import Category, Product
from shopping.serializers import CategorySerializer, ProductSerializer
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
