from django.contrib import admin
from .models import Product, Category, Customer, Order, OrderCategory

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderCategory)
