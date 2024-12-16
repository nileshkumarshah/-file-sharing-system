from rest_framework import authentication
from rest_framework import exceptions
from  rest_framework.authentication import get_authorization_header
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from django.conf import settings
import requests
from django.utils.translation import gettext_lazy as _


class SecondTokenAuthentication(authentication.TokenAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        path = f"{request.path}"
        
        excluded_urls = [
            "/api/user-upload-file",
            
        ]
        if path not in excluded_urls:
            auth_token = request.META.get('HTTP_AUTH_TOKEN', b'')
            if not (auth_token) or not auth or auth[0].lower() != self.keyword.lower().encode():
                return None
            
            verify_token_url = settings.AUTH_URL+"auth/verify_token"
            headers = {
                "auth-token":auth_token,
            }
        
            response = requests.get(
                headers = headers,
                url= verify_token_url,
            )

            if response.status_code in [200, 201]:

                if len(auth) == 1:
                    msg = _('Invalid token header. No credentials provided.')
                    raise exceptions.AuthenticationFailed(msg)
                elif len(auth) > 2:
                    msg = _('Invalid token header. Token string should not contain spaces.')
                    raise exceptions.AuthenticationFailed(msg)

                try:
                    token = auth[1].decode()
                except UnicodeError:
                    msg = _('Invalid token header. Token string should not contain invalid characters.')
                    raise exceptions.AuthenticationFailed(msg)

                return self.authenticate_credentials(token)
            else:
                None
        
        else:
            if not auth or auth[0].lower() != self.keyword.lower().encode():
                return None

            if len(auth) == 1:
                msg = _('Invalid token header. No credentials provided.')
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = _('Invalid token header. Token string should not contain spaces.')
                raise exceptions.AuthenticationFailed(msg)

            try:
                token = auth[1].decode()
            except UnicodeError:
                msg = _('Invalid token header. Token string should not contain invalid characters.')
                raise exceptions.AuthenticationFailed(msg)

            return self.authenticate_credentials(token)
