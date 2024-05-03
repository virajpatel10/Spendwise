from django.urls import path
from . import views
from .views import AddRegularIncome, DeleteIncome, IncomeIndex, EditIncome
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('add-income/', AddRegularIncome.as_view(), name='add-income'),
    path('income-delete/<int:id>/', DeleteIncome.as_view(), name='income-delete'),
    path('', IncomeIndex.as_view(), name='income'),
    path('edit-income/<int:id>/', EditIncome.as_view(), name='income-edit'),
    path('stats', views.income_summary, name="income-stats"),
    path('search-income', csrf_exempt(views.search_income),
         name="search-income"),
    
]
