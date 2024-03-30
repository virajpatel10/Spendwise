from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site

from django.contrib import messages
#from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.urls import reverse
from django.contrib import auth
from django.contrib.sites.shortcuts import get_current_site
#from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
#from django.template.loader import render_to_string
from abc import ABC, abstractmethod


#abstract and inheretance
class BaseAuthView(View):

    @abstractmethod
    def get(self, request):
        pass

    @abstractmethod
    def post(self,request):
        pass

class RegistrationView(BaseAuthView):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        _username = request.POST['username']
        _email = request.POST['email']
        _password = request.POST['password']

        context = {'fieldValues': request.POST}

        if self._create_user(request, _username, _email, _password):
            messages.success(request, 'Account successfully created')
            return render(request, 'authentication/register.html')
        else:
            messages.error(request, 'User registration failed')
            return render(request, 'authentication/register.html', context)

    def _create_user(self, request, username, email, password):
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return False

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                return True
        return False

class UsernameValidationView(BaseAuthView):
    def get(self,request):
        pass 

    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})


class LoginView(BaseAuthView):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        _username = request.POST['username']
        _password = request.POST['password']

        if self._authenticate_user(request, _username, _password):
            return redirect('expenses')
        else:
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html')

    def _authenticate_user(self, request, username, password):
        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, f'Welcome, {user.username}, you are now logged in')
                    return True
                else:
                    messages.error(request, 'Account is not active')
            else:
                messages.error(request, 'Invalid credentials, try again')
        else:
            messages.error(request, 'Please fill all fields')
        return False


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')