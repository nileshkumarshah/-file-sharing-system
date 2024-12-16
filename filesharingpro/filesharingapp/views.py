from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
import os
from .models import *
from .encrypted import *
from datetime import datetime, timedelta
import jwt

JWT_ALGORITHM= 'HS256'
JWT_EXP_DELTA_SECONDS = 85000


# Create your views here.

class ClientUserSignUpAPI(APIView):
    
    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")
        user_type = request.data.get("user_type")
        if CustomUser.objects.filter(email=email).exists():
            return Response({"detail": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create_user(
            username=username, email=email, password=password, user_type=user_type
        )
                
        encrypted_url = encrypt_url(user.id)
        print("encrypted_url", encrypted_url)
        send_mail(
            "Verify your email",
            f"Click the link to verify your email: {settings.FRONTEND_URL}/verify-email/{encrypted_url}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        
        return Response({"detail": "Sign up successful. Verify email to activate account."}, status=status.HTTP_201_CREATED)
        
class ClientUserLoginAPI(APIView):
    
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
    
        if CustomUser.objects.filter(email=email).exists():
            try:
                payload = {
                    'email': email,
                    'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                }
                jwt_token = jwt.encode(payload, 'secret', JWT_ALGORITHM)
                token = jwt_token.decode()
                return Response({"detail": "Login successful.", "token":token}, status=status.HTTP_201_CREATED)
            except Exception as error:
                return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
            
    
class UserUploadFileAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
    
        if request.user.user_type != "operation_user":
            return Response({"detail": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith((".pptx", ".docx", ".xlsx")):
            return Response({"detail": "Invalid file type."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = Files.objects.create(uploader=request.user, file=file)
        return Response({"detail": "File uploaded successfully."}, status=status.HTTP_201_CREATED)
       


class VerifyEmailAPI(APIView):
    def get(self, request, encrypted_url):
        user_id = decrypt_url(encrypted_url)
        if not user_id:
            return Response({"detail": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.email_verified = True
        user.save()
        return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)

class ListFilesAPI(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        if request.user.user_type != "client_user":
            return Response({"detail": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

        files = Files.objects.all()
        file_list = [
            {"id": file.id, "name": os.path.basename(file.file.name), "uploaded_at": file.uploaded_at}
            for file in files
        ]
        return Response({"data":file_list}, status=status.HTTP_200_OK)

class DownloadFileAPI(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request, encrypted_url):
        file_id = decrypt_url(encrypted_url)
    
        if not file_id:
            return Response({"detail": "Invalid download link."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file = Files.objects.get(id=file_id)
        except Files.DoesNotExist:
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.user_type != "client_user":
            return HttpResponseForbidden("You are not authorized to download this file.")
        
        response = Response()
        response["Content-Disposition"] = f"attachment; filename={os.path.basename(file.file.name)}"
        response["X-Accel-Redirect"] = file.file.url
        return response