import uuid

from main_app.models import User
from rest_framework import authentication
from rest_framework import exceptions

class UserAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_TOKEN')
        if not token:
            # TODO: Handle the case when a token is required,
            # but not given by the user.
            return None

        try:
            user = User.objects.get(token=uuid.UUID(token))
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (user, None)
