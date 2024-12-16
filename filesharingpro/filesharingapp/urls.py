from django.urls import path
from . import views

app_name = 'filesharingapp'

urlpatterns = [
    path('api/sign-up', views.ClientUserSignUpAPI.as_view(), name='ClientUserSignUpAPI'),
    path('api/login', views.ClientUserLoginAPI.as_view(), name='ClientUserLoginAPI'),
    path('api/user-upload-file', views.UserUploadFileAPI.as_view(), name='UserUploadFileAPI'), 
    path('api/verify-email/<str:encrypted_url>', views.VerifyEmailAPI.as_view(), name='VerifyEmailAPI'),
    path('api/list-files', views.ListFilesAPI.as_view(), name='ListFilesAPI'),
    path('api/download-file/<str:encrypted_url>', views.DownloadFileAPI.as_view(), name='DownloadFileAPI'),
    
]