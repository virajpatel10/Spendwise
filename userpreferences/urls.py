from . import views
from django.urls import path
from .views import ChangePasswordView

urlpatterns = [
    path('', views.index, name="preferences"),
    
    path('password-change/', ChangePasswordView.as_view(), name='password_change')
]