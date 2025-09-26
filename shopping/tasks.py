from logging import config
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.relations import ObjectDoesNotExist
from celery import shared_task
from shopping.models import Customer, Order
import logging
from django.core.exceptions import ObjectDoesNotExist

@shared_task
def send_email(order_id):
    try:
        admin = Customer.objects.get(is_superuser=True)
        order = Order.objects.get(id=order_id)
    except ObjectDoesNotExist as e
        logger.error("Failed to send email: %s", e)
    send_mail(subject=f"New Order - #{order.id}", message=f"New order has been created. Order id ${order.id}, order details ${order.details}", from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=['test@example.com'], recipient_list=['test@example.com'],)
