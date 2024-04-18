from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json

from .models import Source, UserIncome
from userpreferences.models import UserPreference

def search_income(request):
    if request.method == 'POST':
        search_term = json.loads(request.body).get('searchText')
        incomes = UserIncome.objects.filter(
            amount__istartswith=search_term, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_term, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_term, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_term, owner=request.user)
        result = incomes.values()
        return JsonResponse(list(result), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    sources = Source.objects.all()
    incomes = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    currency_type = UserPreference.objects.get(user=request.user).currency
    context = {
        'incomes': incomes,
        'page_obj': page_obj,
        'currency': currency_type
    }
    return render(request, 'income/index.html', context)

@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)
    
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Income record added successfully')
        return redirect('income')

@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income_record = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income_record,
        'values': income_record,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/edit_income.html', context)

        income_record.amount = amount
        income_record.date = date
        income_record.source = source
        income_record.description = description
        income_record.save()
        messages.success(request, 'Income record updated successfully')
        return redirect('income')

@login_required(login_url='/authentication/login')
def delete_income(request, id):
    income_record = UserIncome.objects.get(pk=id)
    income_record.delete()
    messages.success(request, 'Income record removed')
    return redirect('income')
