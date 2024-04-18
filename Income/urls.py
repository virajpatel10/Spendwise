from django.urls import path
from .views import SearchIncomeView, IndexView, AddIncomeView, IncomeEditView, DeleteIncomeView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('search-income', SearchIncomeView.as_view(),
         name="search_income"),
   path('add_income/', AddIncomeView.as_view(), name='add_income'),
   path('edit_income/<int:pk>/', IncomeEditView.as_view(), name='edit_income'),
   path('income-delete/<int:id>', DeleteIncomeView.as_view(), name="income-delete")
    
]
