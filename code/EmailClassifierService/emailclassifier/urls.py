from django.urls import path
from .views import upload_email
from .views import upload_email_page
from .views import process_uploaded_email

urlpatterns = [
    path("upload-email/", upload_email, name="upload_email"),
    path("upload-page/", upload_email_page, name="upload_email_page"),
    path('process-email/', process_uploaded_email, name='process_email'),
]
