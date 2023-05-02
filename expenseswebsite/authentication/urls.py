from django.urls import path

from authentication.views import RegistrationView

urlpatterns = [
    path('register', RegistrationView.as_view(), name='register')
]
