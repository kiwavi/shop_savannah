from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist  # Correct import
from celery import shared_task
from shopping.models import Customer, Order
import logging
from decouple import config
import json

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email(self, order_id):
    admin = None
    order = None

    try:
        admin = Customer.objects.filter(is_superuser=True, is_active=True).first()
        if not admin:
            logger.error("Activer admin does not exist")
            return

        order = Order.objects.get(id=order_id)

        send_mail(
            subject=f"New Order Alert- #{order.id}",
            message=f"New order alert! Order id {order.id}: Order amount {order.amount}: Order details {json.dumps(order.details, indent=2)}",
            from_email=config("DEFAULT_FROM_EMAIL"),
            recipient_list=[admin.email],
            fail_silently=False,
        )
        logger.info(f"Email for order {order_id} sent")

    except Order.DoesNotExist:
        logger.error(f"Order id {order_id} not found")
        return
    except Exception as exception:
        logger.error(f"Email for order {order_id} has failed: {str(exception)}")
        raise self.retry(exc=exception, countdown=60)
