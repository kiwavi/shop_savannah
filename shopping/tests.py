from django.test import TestCase
from shopping.models import Category, Product, Order, OrderCategory, Customer
from django.core.exceptions import ValidationError

# Create your tests here.


class OrderAmountPositive(TestCase):
    def test_order_amount_positive(self):
        customer = Customer.objects.create(
            email="dmunyiri12@gmail.com", phone_number="+254742477460"
        )
        order = Order(customer=customer, details="[]", amount=-1)

        with self.assertRaises(ValidationError):
            order.full_clean()
            order.save()


class CategoryQuantityIsPositive(TestCase):
    def test_category_quantity_is_positive(self):
        product = Product.objects.create(
            name="Bedroom furniture", description="Stuff that belongs to the bedroom"
        )
        category = Category(
            name="Bedding",
            description="Bedroom furniture",
            quantity=0,
            price=10,
            product=product,
        )

        with self.assertRaises(ValidationError):
            category.full_clean()
            category.save()


class CategoryPriceIsPositive(TestCase):
    def test_category_price_is_positive(self):
        product = Product.objects.create(
            name="Bedroom furniture", description="Stuff that belongs to the bedroom"
        )
        category = Category(
            name="Bedding",
            description="Bedroom furniture",
            quantity=10,
            price=0,
            product=product,
        )

        with self.assertRaises(ValidationError):
            category.full_clean()
            category.save()


class CustomerTestPhoneNumber(TestCase):
    def test_customer_phone_number_format(self):
        customer = Customer(
            email="dmunyiri12@gmail.com",
            phone_number="+254742477")

        with self.assertRaises(ValidationError):
            customer.full_clean()
            customer.save()


class OrdersTestUniqueIndex(TestCase):
    def test_orders_unique_index(self):
        customer = Customer.objects.create(
            email="dmunyiri12@gmail.com", phone_number="+254742477460"
        )
        order = Order.objects.create(
            customer=customer, amount=100, details="[]")
        product = Product.objects.create(
            name="Bedroom furniture", description="Stuff that belongs to the bedroom"
        )
        category = Category.objects.create(
            name="Bedding",
            description="Bedroom furniture",
            quantity=10,
            price=10,
            product=product,
        )
        order_category = OrderCategory.objects.create(
            quantity=10, category=category, order=order, customer=customer
        )
        order_category_2 = OrderCategory(
            quantity=10, category=category, order=order, customer=customer
        )

        with self.assertRaises(ValidationError):
            order_category_2.full_clean()
            order_category_2.save()
