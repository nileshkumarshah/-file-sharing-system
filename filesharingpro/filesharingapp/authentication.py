import jwt
from django.utils.encoding import smart_str
from django.utils.translation import gettext
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework.permissions import BasePermission
from rest_framework.authentication import BaseAuthentication
from .models import CustomUser
from datetime import datetime



def jwt_get_user_id_from_payload_handler(payload):
    """
    Override this function if user_id is formatted differently in payload
    """
    return payload.get('email')


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.
    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


def authenticate_credentials(payload):
    """
    Returns an active user that matches the payload's user id and email.
    """
    userId = jwt_get_user_id_from_payload_handler(payload)
    # userId = payload
    user = None
    if not userId:
        msg = gettext('Invalid payload.')
        raise exceptions.AuthenticationFailed(msg)
    try:
        print("email", userId)
        user = CustomUser.objects.get(email__exact=userId)
        print(user)
    except CustomUser.DoesNotExist:
        msg = gettext('Invalid signature.')
        raise exceptions.AuthenticationFailed(msg)
    print(user)
    return user


class JSONWebTokenAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    """
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()
        auth_header_prefix = 'bearer'
        if not auth:
            if None:
                return request.COOKIES.get(None)
            return None
        if smart_str(auth[0].lower()) != auth_header_prefix:
            return None
        if len(auth) == 1:
            msg = gettext('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = gettext('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        jwt_value = auth[1]
        if jwt_value is None:
            return None
        try:
            payload = jwt.decode(jwt_value, verify=False)
            time = payload.get('exp')
            dt_object = datetime.fromtimestamp(time)
            if dt_object <= datetime.now():
                msg = gettext('Signature has expired.')
                raise exceptions.AuthenticationFailed(msg)
        except jwt.ExpiredSignature:
            msg = gettext('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = gettext('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()
        user = authenticate_credentials(payload)
        request.user = user
        return user, jwt_value


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        try:
            if request.user.id:
                return True
        except:
            msg = gettext('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)


class AllowAny(BasePermission):
    def has_permission(self, request, view):
        return True


class IsAdmin(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        try:
            if request.user.is_admin:
                return True
        except:
            msg = gettext('Invalid Authorization header. No Admin credentials provided.')
            raise exceptions.AuthenticationFailed(msg)