from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Product (models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Category (models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="categories")
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="quantities_positive_int"
            ),
            models.CheckConstraint(
                check=models.Q(price__gt=0),
                name="price_positive"
            )
        ]

    def __str__(self):
        return self.name

class Customer (models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(region="KE", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

class Order (models.Model):
   id = models.BigAutoField(primary_key=True)
   customer = models.ForeignKey(Customer, on_delete=models.CASCADE,related_name="orders")
   details = models.JSONField()
   amount = models.DecimalField(max_digits=10, decimal_places=2)
   created_at = models.DateTimeField(auto_now_add=True)
   deleted_at = models.DateTimeField(null=True,blank=True)
   updated_at = models.DateTimeField(auto_now=True)
   categories = models.ManyToManyField(Category, through= "OrderCategory",related_name="orders")

   class Meta:
      constraints = [
         models.CheckConstraint(
            check=models.Q(amount__gte=0),
            name="amount_as_positive"
         )
      ]

class OrderCategory (models.Model):
    id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,related_name="customer_orders")
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "order", "category"],
                name="unique_customer_order_category",
                condition=models.Q(order__isnull=False)   # only enforce when order_id is not null
            ),
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="quantity_positive_int"
            )
        ]
