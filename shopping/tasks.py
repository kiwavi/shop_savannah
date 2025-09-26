from logging import config
from django.core.mail import send_mail
from rest_framework.relations import ObjectDoesNotExist
from celery import shared_task
from shopping.models import Customer, Order
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email(self, order_id):
    try:
        admin = Customer.objects.get(is_superuser=True, is_active=True).first()
        order = Order.objects.get(id=order_id)
    except ObjectDoesNotExist as e:
        logger.error("Failed to send email: %s", e)
    try:
        send_mail(
            subject=f"New Order - #{order.id}",
            message=f"New order has been created. Order id ${order.id}, order details ${order.details}",
            from_email=config("DEFAULT_FROM_EMAIL"),
            recipient_list=admin["email"],
        )
    except Exception as exception:
        logger.error(f"Failed to send email for order {order_id}: {str(exception)}")
        raise self.retry(exc=exception, countdown=60)
