from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

# Create your models here.

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("operation_user", "User"),
        ("client_user", "Client"),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    email_verified = models.BooleanField(default=False)

class Files(models.Model):
    uploader = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
