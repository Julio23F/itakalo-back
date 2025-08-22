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
from django.contrib.auth.models import User
from config import settings
from member.models import Member
from member.serializers import MemberSerializer


class BaseJSONWebTokenAuthentication(BaseAuthentication):
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
        except jwt.ExpiredSignatureError:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        member = self.authenticate_credentials(payload)
        return member, jwt_value

    def authenticate_credentials(self, payload):
        """
        Returns an active member that matches the payload's member id and email.
        """
        payload_member = payload
        if not payload_member:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        # Check admin user
        if ('is_superuser' in payload_member) and payload_member['is_superuser']:
            try:
                admin = User.objects.get(id=payload_member['id'])
            except User.DoesNotExist:
                msg = _('Invalid signature.')
                raise exceptions.AuthenticationFailed(msg)

            return admin
        
        try:
            # Check general member
            member = Member.objects.filter(id=payload_member['id']).first()
            if member:
                member.is_authenticated = True
                return member
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)
        except Member.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)


class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = settings.JWT_AUTH['JWT_AUTH_HEADER_PREFIX'].lower()
        if not auth:
            if settings.JWT_AUTH['JWT_AUTH_COOKIE']:
                return request.COOKIES.get(settings.JWT_AUTH['JWT_AUTH_COOKIE'])
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
        return '{0} realm="{1}"'.format(settings.JWT_AUTH['JWT_AUTH_HEADER_PREFIX'], self.www_authenticate_realm)


def jwt_get_secret_key(payload=None):
    """
    For enhanced security you may want to use a secret key based on member.

    This way you have an option to logout only this member if:
        - token is compromised
        - password is changed
        - etc.
    """
    if settings.JWT_AUTH['JWT_GET_USER_SECRET_KEY']:
        member = Member.objects.get(id=payload.get('id'))
        key = str(settings.JWT_AUTH['JWT_GET_USER_SECRET_KEY'](member))
        return key
    return settings.JWT_AUTH['JWT_SECRET_KEY']


def jwt_payload_handler(member):
    email_field = 'email'
    email = member.email

    warnings.warn(
        'The following fields will be removed in the future: '
        '`email` and `id`. ',
        DeprecationWarning
    )
    exp = datetime.utcnow() + settings.JWT_AUTH['JWT_EXPIRATION_DELTA']
    payload = {
        'id': member.id,
        'email': email,
        'type': member.type,
        'first_name': member.first_name,
        'last_name': member.last_name,
        'telnumber': member.telnumber,
        'image': member.image,
        'exp': exp,
    }
    if hasattr(member, 'email'):
        payload['email'] = member.email
    if isinstance(member.id, uuid.UUID):
        payload['id'] = str(member.id)

    payload[email_field] = email

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if settings.JWT_AUTH['JWT_ALLOW_REFRESH']:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if settings.JWT_AUTH['JWT_AUDIENCE'] is not None:
        payload['aud'] = settings.JWT_AUTH['JWT_AUDIENCE']

    if settings.JWT_AUTH['JWT_ISSUER'] is not None:
        payload['iss'] = settings.JWT_AUTH['JWT_ISSUER']

    return payload


def jwt_get_id_from_payload_handler(payload):
    """
    Override this function if id is formatted differently in payload
    """
    warnings.warn(
        'The following will be removed in the future. '
        'Use `JWT_PAYLOAD_GET_USERNAME_HANDLER` instead.',
        DeprecationWarning
    )

    return payload.get('id')


def jwt_get_email_from_payload_handler(payload):
    """
    Override this function if email is formatted differently in payload
    """
    return payload.get('email')


def jwt_encode_handler(payload):
    key = settings.JWT_AUTH['JWT_PRIVATE_KEY'] or jwt_get_secret_key(payload)
    # return jwt.encode(
    #     payload,
    #     key,
    #     settings.JWT_AUTH['JWT_ALGORITHM']
    # ).decode('utf-8')
    return jwt.encode(
        payload,
        key,
        settings.JWT_AUTH['JWT_ALGORITHM']
    )


def jwt_decode_handler(token):    
    options = {
        'verify_exp': settings.JWT_AUTH['JWT_VERIFY_EXPIRATION'],
    }
    
    # get member from token, BEFORE verification, to get member secret key
    
    # unverified_payload = jwt.decode(token, None, False)
    
    unverified_payload = jwt.decode(
        token,
        options={"verify_signature": False}
    )

    
    secret_key = jwt_get_secret_key(unverified_payload)
    
    
    # str_token = token.decode('utf-8').strip()
    str_token = str(token, 'utf-8').strip()
    
    
    # res = jwt.decode(
    #     str_token,
    #     settings.JWT_AUTH['JWT_PUBLIC_KEY'] or secret_key,
    # trop d'argument algorithms, vu que ce n'est pas nommée alors que la 3em position est pour algorithms
    #     # settings.JWT_AUTH['JWT_VERIFY'],
    #     options=options,
    #     leeway=settings.JWT_AUTH['JWT_LEEWAY'],
    #     audience=settings.JWT_AUTH['JWT_AUDIENCE'],
    #     issuer=settings.JWT_AUTH['JWT_ISSUER'],
    #     algorithms=[settings.JWT_AUTH['JWT_ALGORITHM']]
    # )
    res = jwt.decode(
        str_token,
        key=settings.JWT_AUTH['JWT_PUBLIC_KEY'] or secret_key,
        algorithms=[settings.JWT_AUTH['JWT_ALGORITHM']],
        options=options,
        leeway=settings.JWT_AUTH['JWT_LEEWAY'],
        audience=settings.JWT_AUTH['JWT_AUDIENCE'],
        issuer=settings.JWT_AUTH['JWT_ISSUER'],
    )

    return res


def jwt_response_payload_handler(token, member=None, request=None):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the Member.

    Example:

    def jwt_response_payload_handler(token, member=None, request=None):
        return {
            'token': token,
            'member': MemberSerializer(member, context={'request': request}).data
        }

    """
    return {
        'token': token,
        'member': member,
    }
