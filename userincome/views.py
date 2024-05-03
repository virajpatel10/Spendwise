from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.views import View
from .models import Source, UserIncome
from userpreferences.models import UserPreference
from django.utils.decorators import method_decorator

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

class BaseIncomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request,'income/stats.html')

    def post(self, request, *args, **kwargs):
        raise NotImplementedError("Subclasses must override post() method")

    def get_context_data(self, request, **kwargs):
        raise NotImplementedError("Subclasses must override get_context_data() method")

# Concrete class for adding regular income
class AddRegularIncome(BaseIncomeView):
    template_name = 'income/add_income.html'
    def get(self, request, *args, **kwargs):
        sources = Source.objects.all()
        context = {
            'sources': sources,
            'values': request.POST
        }
        return render(request,'income/add_income.html',context)
    
    def post(self, request, *args, **kwargs):
        
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not all([amount, description, date, source]):
            messages.error(request, 'All fields are required.')
            return render(request, self.template_name, self.get_context_data())

        UserIncome.objects.create(
            amount=amount, description=description, date=date, source=source, owner=request.user
        )
        messages.success(request, 'Regular income added successfully')
        return redirect('income')

    def get_context_data(self, request, **kwargs):
        sources = Source.objects.all()
        return {
            'sources': sources,
            'values': kwargs.get('values', {})
        }

# Class for managing income deletion
class DeleteIncome(BaseIncomeView):
    def get(self, request, id, *args, **kwargs):
        income_record = UserIncome.objects.get(pk=id)
        print(income_record)
        income_record.delete()
        messages.success(request, 'Income record removed')
        return redirect('income')

    def get_context_data(self, **kwargs):
        return {}


# Class for displaying the index page with paginated incomes
class IncomeIndex(BaseIncomeView):
    template_name = 'income/index.html'

    @method_decorator(login_required(login_url='/authentication/login'))
    def get_context_data(self, request, **kwargs):
        incomes = UserIncome.objects.filter(owner=self.request.user).order_by('date')
        paginator = Paginator(incomes, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        currency_type = UserPreference.objects.get(user=self.request.user).currency

        return {
            'incomes': incomes,
            'page_obj': page_obj,
            'currency': currency_type
        }
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        sources = Source.objects.all()
        incomes = UserIncome.objects.filter(owner=request.user).order_by('date')

        print(incomes)

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

# Class for editing an existing income
class EditIncome(BaseIncomeView):
    template_name = 'income/edit_income.html'

    @method_decorator(login_required(login_url='/authentication/login'))
    def get_context_data(self, id, request, **kwargs):
        income = UserIncome.objects.get(pk=id, owner=self.request.user)
        sources = Source.objects.all()
        return {
            'income': income,
            'sources': sources,
            'values': income.__dict__
        }
    def get(self, request, id, *args, **kwargs):
        income_record = UserIncome.objects.get(pk=id)
        sources = Source.objects.all()
        context = {
            'income': income_record,
            'values': income_record,
            'sources': sources
        }
        return render(request, 'income/edit_income.html', context)

    @method_decorator(login_required(login_url='/authentication/login'))
    def post(self, request, id, *args, **kwargs):
        income = UserIncome.objects.get(pk=id, owner=request.user)
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not all([amount, description, date, source]):
            messages.error(request, 'All fields are required.')
            return render(request, self.template_name, self.get_context_data(id=id))

        income.amount = amount
        income.description = description
        income.date = date
        income.source = source
        income.save()
        messages.success(request, 'Income updated successfully')
        return redirect('income')
    

@login_required(login_url='/authentication/login')
def income_summary(request):
    incomes = UserIncome.objects.filter(owner=request.user).order_by('date')
    income_dates = [income.date.isoformat() for income in incomes]
    # Extract dates and amounts for the chart
    #income_dates = list(incomes.values_list('date', flat=True))
    income_amounts = list(incomes.values_list('amount', flat=True))

    paginator = Paginator(incomes, 5)  # Adjust the page size as needed
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    currency_type = UserPreference.objects.get(user=request.user).currency

    context = {
        'page_obj': page_obj,
        'currency': currency_type,
        'income_dates': json.dumps(income_dates),  # Serialize for JSON
        'income_amounts': json.dumps(income_amounts)  # Serialize for JSON
    }
    
    return render(request, 'income/stats.html', context)

'''
@login_required(login_url='/authentication/login')
def index(request):
    sources = Source.objects.all()
    incomes = UserIncome.objects.filter(owner=request.user).order_by('date')

    print(incomes)

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


@login_required(login_url='/authentication/login')
def income_summary(request):
    incomes = UserIncome.objects.filter(owner=request.user).order_by('date')
    income_dates = [income.date.isoformat() for income in incomes]
    # Extract dates and amounts for the chart
    #income_dates = list(incomes.values_list('date', flat=True))
    income_amounts = list(incomes.values_list('amount', flat=True))

    paginator = Paginator(incomes, 5)  # Adjust the page size as needed
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    currency_type = UserPreference.objects.get(user=request.user).currency

    context = {
        'page_obj': page_obj,
        'currency': currency_type,
        'income_dates': json.dumps(income_dates),  # Serialize for JSON
        'income_amounts': json.dumps(income_amounts)  # Serialize for JSON
    }
    
    return render(request, 'income/stats.html', context)'''