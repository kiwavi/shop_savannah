from django.urls import path,include
from . import views
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'products', ProductsViewSet, basename='products')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'cart', OrderCategoryViewSet, basename='cart')

urlpatterns = [
    path("", views.index, name="index"),
    path("api/v1/", include(router.urls)),
]
