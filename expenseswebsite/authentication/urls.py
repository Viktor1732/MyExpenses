from django.urls import path

from .views import RegistrationView, UsernameValidationView, EmailValidationView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
    path('register', RegistrationView.as_view(), name='register'),
    path('activate/<uidb64>/<token>', RegistrationView.as_view(), name='activate'),
]
