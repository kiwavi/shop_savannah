from django.test import TestCase
from shopping.models import Category, Product, Order, OrderCategory, Customer
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status

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
        customer = Customer(email="dmunyiri12@gmail.com", phone_number="+254742477")

        with self.assertRaises(ValidationError):
            customer.full_clean()
            customer.save()


class OrdersTestUniqueIndex(TestCase):
    def test_orders_unique_index(self):
        customer = Customer.objects.create(
            email="dmunyiri12@gmail.com", phone_number="+254742477460"
        )
        order = Order.objects.create(customer=customer, amount=100, details="[]")
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


class TestOrderCreation(APITestCase):
    customer = None
    def setUp(self):
        self.customer = Customer.objects.create_user(
            email="customer@customer.com",
            password="shopperpass1"
        )
        customer = self.customer
        self.client.force_authenticate(user=self.customer)

    def test_create_order_via_api(self):
        product = Product.objects.create(name="Testproduct",description="Test description")
        category = Category.objects.create(name="Testcategory1", description="Test category1 description",price=5,quantity=5,product=product)
        cart = OrderCategory.objects.create(quantity=2,category=category,customer=self.customer)

        url = '/shopping/api/v1/order/'
        data = {
            'details': {"phone_number": "0742477460", "address": "Right there"}
        }
        response = self.client.post(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_out_of_stock(self):
        product = Product.objects.create(name="Testproduct",description="Test description")
        category = Category.objects.create(name="Testcategory1", description="Test category1 description",price=5,quantity=5,product=product)
        cart = OrderCategory.objects.create(quantity=6,category=category,customer=self.customer)

        url = '/shopping/api/v1/order/'
        data = {
            'details': {"phone_number": "0742477460", "address": "Right there"}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
