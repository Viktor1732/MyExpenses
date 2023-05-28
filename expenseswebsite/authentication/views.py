import json

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.contrib.auth.models import User
from validate_email import validate_email
from .utils import account_activation_token


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

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        # Используется для сохранения уже введенных данных в форму.
        context = {
            'fieldValues': request.POST,
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Пароль слишком короткий!')
                    return render(request, 'authentication/register.html', context=context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))  # Кодируем пользователя для безопасной отправки
                domain = get_current_site(request).domain
                link = reverse('activate',
                               kwargs={'uidb64': uidb64, 'token': account_activation_token.make_token(user)})
                activate_url = 'http://' + domain + link

                email_subject = 'Активация Вашего аккаунта'
                email_body = 'Приветствую тебя ' + user.username + '! Для окончания регистрации \
                и активации аккаунта пройди по этой ссылке:\n' + activate_url + '\n' + '\n' + 'Если вы считаете,\
                что данное сообщение послано вам ошибочно, просто проигнорируйте его.'
                email = EmailMessage(
                    email_subject,
                    email_body,
                    "noreply@semycolon.com",
                    [email],
                )
                email.send(fail_silently=False)
                messages.success(request, 'Аккаунт успешно создан!')
                return render(request, 'authentication/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64).decode())  # Декодируем пользователя
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login' + '?message=' + 'Аккаунт уже активирован!')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Аккаунт активирован успешно!')
            return redirect('login')

        except Exception as ex:
            pass

            return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
