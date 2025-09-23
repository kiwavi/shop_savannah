from django.db.models.base import ObjectDoesNotExist
from shopping.models import Customer


def oidc_login_resolver(request,token):
    if not token.get("email"):
        raise ValueError("Email not passed")

    if not token.get("name"):
        raise ValueError("Name not passed")

    email = token.get("email")
    name = token.get("name")

   return Customer.objects.get_or_create(email=email,name=name)
