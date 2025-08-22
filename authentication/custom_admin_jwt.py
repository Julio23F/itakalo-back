from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import jwt
import uuid
import warnings
from calendar import timegm
from datetime import datetime
from rest_framework import exceptions
# from rest_framework_jwt.settings import api_settings
from django.utils.encoding import smart_str
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)
from django.utils.translation import gettext_lazy as _
from config import settings
from .custom_jwt import jwt_decode_handler

def custom_admin_authentication(request, email, password):
  return authenticate(request, email=email, password=password)


class AdminBaseJSONWebTokenAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    """

    def get_jwt_value(self, request):
        pass

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None
        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignatureErrorError:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)
        return user, jwt_value

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        payload_user = payload

        if not payload_user:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(id=payload_user['id'])
        except User.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        if user.leave_date:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)
        user.is_authenticated = True
        return user


class AdminJSONWebTokenAuthentication(AdminBaseJSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = settings.ADMIN_JWT_AUTH['JWT_AUTH_HEADER_PREFIX'].lower()
        if not auth:
            if settings.ADMIN_JWT_AUTH['JWT_AUTH_COOKIE']:
                return request.COOKIES.get(settings.ADMIN_JWT_AUTH['JWT_AUTH_COOKIE'])
            return None

        if smart_str(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(settings.ADMIN_JWT_AUTH['JWT_AUTH_HEADER_PREFIX'], self.www_authenticate_realm)


def admin_jwt_get_secret_key(payload=None):
    """
    For enhanced security you may want to use a secret key based on user.

    This way you have an option to logout only this user if:
        - token is compromised
        - password is changed
        - etc.
    """
    if settings.ADMIN_JWT_AUTH['JWT_GET_USER_SECRET_KEY']:
        # User = get_user_model()  # noqa: N806
        user = User.objects.get(id=payload.get('id'))
        key = str(settings.ADMIN_JWT_AUTH['JWT_GET_USER_SECRET_KEY'](user))
        return key
    return settings.ADMIN_JWT_AUTH['JWT_SECRET_KEY']


def admin_jwt_payload_handler(user):
    email_field = 'email'
    email = user.email

    warnings.warn(
        'The following fields will be removed in the future: '
        '`email` and `id`. ',
        DeprecationWarning
    )
    exp = datetime.utcnow() + settings.ADMIN_JWT_AUTH['JWT_EXPIRATION_DELTA']
    payload = {
        'id': user.id,
        'email': email,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'exp': exp
    }
    if hasattr(user, 'email'):
        payload['email'] = user.email
    if isinstance(user.id, uuid.UUID):
        payload['id'] = str(user.id)

    payload[email_field] = email

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if settings.ADMIN_JWT_AUTH['JWT_ALLOW_REFRESH']:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if settings.ADMIN_JWT_AUTH['JWT_AUDIENCE'] is not None:
        payload['aud'] = settings.ADMIN_JWT_AUTH['JWT_AUDIENCE']

    if settings.ADMIN_JWT_AUTH['JWT_ISSUER'] is not None:
        payload['iss'] = settings.ADMIN_JWT_AUTH['JWT_ISSUER']

    return payload


def admin_jwt_get_id_from_payload_handler(payload):
    """
    Override this function if id is formatted differently in payload
    """
    warnings.warn(
        'The following will be removed in the future. '
        'Use `JWT_PAYLOAD_GET_USERNAME_HANDLER` instead.',
        DeprecationWarning
    )

    return payload.get('id')


def admin_jwt_get_email_from_payload_handler(payload):
    """
    Override this function if email is formatted differently in payload
    """
    return payload.get('email')


def admin_jwt_encode_handler(payload):
    key = settings.ADMIN_JWT_AUTH['JWT_PRIVATE_KEY'] or admin_jwt_get_secret_key(payload)
    return jwt.encode(
        payload,
        key,
        settings.ADMIN_JWT_AUTH['JWT_ALGORITHM']
    ).decode('utf-8')


def admin_jwt_decode_handler(token):
    options = {
        'verify_exp': settings.ADMIN_JWT_AUTH['JWT_VERIFY_EXPIRATION'],
    }
    # get user from token, BEFORE verification, to get user secret key
    unverified_payload = jwt.decode(token, None, False)
    secret_key = admin_jwt_get_secret_key(unverified_payload)
    # str_token = token.decode('utf-8').strip()
    str_token = str(token, 'utf-8').strip()
    res = jwt.decode(
        str_token,
        settings.ADMIN_JWT_AUTH['JWT_PUBLIC_KEY'] or secret_key,
        settings.ADMIN_JWT_AUTH['JWT_VERIFY'],
        options=options,
        leeway=settings.ADMIN_JWT_AUTH['JWT_LEEWAY'],
        audience=settings.ADMIN_JWT_AUTH['JWT_AUDIENCE'],
        issuer=settings.ADMIN_JWT_AUTH['JWT_ISSUER'],
        algorithms=[settings.ADMIN_JWT_AUTH['JWT_ALGORITHM']]
    )
    return res


def admin_jwt_response_payload_handler(token, user=None, request=None):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the User.

    Example:

    def jwt_response_payload_handler(token, user=None, request=None):
        return {
            'token': token,
            'user': UserSerializer(user, context={'request': request}).data
        }

    """
    return {
        'token': token,
        'user': user,
    }
