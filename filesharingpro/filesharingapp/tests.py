from django.test import TestCase
from django.urls import reverse
from .models import CustomUser, Files
from .encrypted import *
from datetime import datetime, timedelta
import jwt
from django.core.mail import send_mail

# Create your tests here.


class ClientUserSignUpAPITestCase(TestCase):
    def setUp(self):
        # Create a test user
        email = "sotib232@chosenx.com",
        username = "son1",
        password = "1234",
        user_type = "client_user"

        self.user = CustomUser.objects.create_user(username=username, email=email, password=password, user_type=user_type)
        encrypted_url = encrypt_url(self.user.id)
        send_mail(
            "Verify your email",
            f"Click the link to verify your email: {settings.FRONTEND_URL}/verify-email/{encrypted_url}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

    def test_user_list(self):
        response = self.client.get(reverse('user-list'))  
        self.assertEqual(response.status_code, 200)
        
class ClientUserLoginAPITestCase(TestCase):
    def setUp(self):
        
        import jwt

        payload = {
            "exp": 9999999999,
            "email": "sotibi18232@chosenx.com",
            "password": "1234",
        }
        SECRET_KEY = "SECRET_KEY"

        self.jwt = jwt.encode(payload, SECRET_KEY)
        
    def test_user_list(self):
        
        data1= {"email": "sotibi18232@chosenx.com",
            "password": "1234"}
        resp1 = self.client.post(
            "/api/login",
            HTTP_AUTHORIZATION=f"Bearer {self.jwt}",
            data=data1,
        )
        self.assertEqual(resp1.status_code, 403)
        

        
