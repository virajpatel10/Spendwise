from .views import RegistrationView, LogoutView, LoginView, UsernameValidationView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('signup', RegistrationView.as_view(), name="Register"),
    path('login', LoginView.as_view(), name="Login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()),
         name="validate-username"),
]