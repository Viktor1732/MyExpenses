import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User
from validate_email import validate_email


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse(
                {'username_error': 'Имя пользователя должно содержать только строчные буквы!'}, status=400
            )
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {'username_error': 'Имя пользователя уже существует. Выберите другое имя!'}, status=409
            )
        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse(
                {'email_error': 'Email недействителен!'}, status=400
            )
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {'email_error': 'Этот email уже зарегистрирован!'}, status=409
            )
        return JsonResponse({'email_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
