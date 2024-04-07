from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
#from userpreferences.models import UserPreference
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
    #currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        #'currency': currency
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
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(
        owner=request.user,
        date__gte=six_months_ago, 
        date__lte=todays_date
    ).values('category').annotate(total_amount=Sum('amount')).order_by('-total_amount')

    finalrep = {expense['category']: expense['total_amount'] for expense in expenses}
    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def stats_view(request):
    '''
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    total_expenses_last_six_months = Expense.objects.filter(
        owner=request.user,
        date__gte=six_months_ago, 
        date__lte=todays_date
    ).aggregate(Sum('amount'))

    # You can add more context as needed
    context = {
        'total_expenses_last_six_months': total_expenses_last_six_months['amount__sum'] or 0,
    }'''
    
    return render(request, 'expenses/stats.html')