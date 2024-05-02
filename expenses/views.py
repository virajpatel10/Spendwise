from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from userpreferences.models import UserPreference
import datetime

def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        _expenses = Expense.objects.filter(
            _amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            _date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            _description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            _category__icontains=search_str, owner=request.user)
        _data = _expenses.values()
        return JsonResponse(list(_data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    exists = UserPreference.objects.filter(user=request.user).exists()
    if exists:
        currency = UserPreference.objects.get(user=request.user).currency
    else:
        return redirect('preferences')
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
    }
    return render(request, 'expenses/index.html', context)

def _validate_expense_data(post_data):
    """Validates the required fields in the POST data."""
    required_fields = ['amount', 'description', 'expense_date', 'category']
    for field in required_fields:
        if not post_data.get(field):
            return False, f"{field.replace('_', ' ').capitalize()} is required"
    # Additional validation logic can be added here (e.g., checking for numeric values)
    return True, None

@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    try:
        expense = Expense.objects.get(pk=id, owner=request.user)  # Ensure the expense belongs to the logged-in user
    except ObjectDoesNotExist:
        messages.error(request, 'Expense not found.')
        return redirect('expenses')
    
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)

    if request.method == 'POST':
        is_valid, error_message = _validate_expense_data(request.POST)
        if not is_valid:
            messages.error(request, error_message)
            return render(request, 'expenses/edit-expense.html', context)
        
        # Update the expense with validated data
        expense.amount = request.POST['amount']
        expense.date = request.POST['expense_date']
        expense.category = request.POST['category']
        expense.description = request.POST['description']
        expense.save()

        messages.success(request, 'Expense updated successfully')
        return redirect('expenses')
    

@login_required(login_url='/authentication/login')
def add_expense(request):
    _categories = Category.objects.all()
    context = {
        'categories': _categories,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        # Use the helper function to validate data
        is_valid, error_message = _validate_expense_data(request.POST)
        if not is_valid:
            messages.error(request, error_message)
            return render(request, 'expenses/add_expense.html', context)
        
        # Data has passed validation
        Expense.objects.create(
            owner=request.user,
            amount=request.POST['amount'],
            date=request.POST['expense_date'],
            category=request.POST['category'],
            description=request.POST['description']
        )
        messages.success(request, 'Expense saved successfully')
        return redirect('expenses')
    
@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    try:
        expense = Expense.objects.get(pk=id, owner=request.user)  # Ensure the expense belongs to the logged-in user
    except ObjectDoesNotExist:
        messages.error(request, 'Expense not found.')
        return redirect('expenses')
    
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)

    if request.method == 'POST':
        is_valid, error_message = _validate_expense_data(request.POST)
        if not is_valid:
            messages.error(request, error_message)
            return render(request, 'expenses/edit-expense.html', context)
        
        # Update the expense with validated data
        expense.amount = request.POST['amount']
        expense.date = request.POST['expense_date']
        expense.category = request.POST['category']
        expense.description = request.POST['description']
        expense.save()

        messages.success(request, 'Expense updated successfully')
        return redirect('expenses')
    

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')