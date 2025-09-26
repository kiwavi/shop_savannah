from django.db.models.base import ObjectDoesNotExist
from shopping.models import Customer
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

class customerExtendedOIDC(OIDCAuthenticationBackend):
    def filter_users_by_claims(self,claims):
        email = claims.get('email')
        if not email:
            return self.UserModel.objects.none()
        try:
            return Customer.objects.filter(email=email)
        except ObjectDoesNotExist:
            return []

    def create_user(self,claims):
        return Customer.objects.create(email=claims.get("email"))
