from django.core import validators
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class CustomerManager(BaseUserManager):
    def create_user(self, email, phone_number=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Customers must have an email")
        email = self.normalize_email(email)
        customer = self.model(email=email, phone_number=phone_number, **extra_fields)
        customer.set_password(password)
        customer.save(using=self._db)
        return customer

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password=password, **extra_fields)


def positiveValidator(val):
    if val <= 0:
        raise ValidationError("Value must be a positive integer")


# Create your models here.
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    quantity = models.IntegerField(validators=[positiveValidator])
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[positiveValidator]
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="categories"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=0), name="quantities_positive_int"
            ),
            models.CheckConstraint(check=models.Q(price__gt=0), name="price_positive"),
        ]

    def __str__(self):
        return self.name


class Customer(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(region="KE", unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomerManager()

    def __str__(self):
        return self.email


class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    details = models.JSONField()
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[positiveValidator]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(
        Category, through="OrderCategory", related_name="orders"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0), name="amount_as_positive"
            )
        ]


class OrderCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField(validators=[positiveValidator])
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="customer_orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "order", "category"],
                name="unique_customer_order_category",
                condition=models.Q(
                    order__isnull=False
                ),  # only enforce when order_id is not null
            ),
            models.CheckConstraint(
                check=models.Q(quantity__gt=0), name="quantity_positive_int"
            ),
        ]
