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
        email = "stib232@chosenx.com",
        username = "Baba",
        password = "1234",
        user_type = "client_user"

        user = CustomUser(username=username, email=email, password=password, user_type=user_type)
        user.save(force_insert=True)
        encrypted_url = encrypt_url(user.id)
        send_mail(
            "Verify your email",
            f"Click the link to verify your email: {settings.FRONTEND_URL}/verify-email/{encrypted_url}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

    def test_user_signup(self):
        data1 = {
                "email": "sotibi18232@chosenx.com",
                "username": "sonu",
                "password": "1234",
                "user_type": "client_user"
            }
        response = self.client.post(
            "/api/sign-up",
            data=data1,
        ) 
        self.assertEqual(response.status_code, 201)
        
class ClientUserLoginAPITestCase(TestCase):
    def setUp(self):
        
        import jwt

        payload = {
            "exp": 9999999999,
            "email": "stib232@chosenx.com"
        }
        SECRET_KEY = "SECRET_KEY"

        self.jwt = jwt.encode(payload, SECRET_KEY)
        self.token = self.jwt.decode()
        print('token', self.token)
        
    def test_user_login(self):
        
        data1= {"email": "stib232@chosenx.com",
            "password": "1234"}
        resp1 = self.client.post(
            "/api/login",
            data=data1,
        )
        self.assertEqual(resp1.status_code, 400)
        
class UserUploadFileAPITestCase(TestCase):
    
    def setUp(self):
        
        import jwt

        payload = {
            "exp": 9999999999,
            "email": "stib232@chosenx.com"
        }
        SECRET_KEY = "SECRET_KEY"

        self.jwt = jwt.encode(payload, SECRET_KEY)
        self.token = self.jwt.decode()
    
    def test_upload_file(self):
        
        data1 = {
            "file": "/home/nilesh/NewFolder/project/INDUS_Documents_Script/Documenttobeupload.xlsx"
        }
        
        resp = self.client.post(
            "/api/user-upload-file",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            data=data1,
        )
        self.assertEqual(resp.status_code, 403)
        
        
        resp1 = self.client.post(
            "/api/user-upload-file",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            data=data1,
        )
        self.assertEqual(resp1.status_code, 201)
        

        
        
        
