from .views import RegistrationView, LogoutView, LoginView, UsernameValidationView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('signup', RegistrationView.as_view(), name="signup"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()),
         name="validate-username"),
]