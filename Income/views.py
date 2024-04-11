from django.views import View
from django.http import JsonResponse
import json
from .models import IncomeSource, IncomeRecord
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.shortcuts import redirect
#from userpreferences.models import UserPreference

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django import forms
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import FormView


class SearchIncomeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        search_str = json.loads(request.body).get('searchText')
        __income = IncomeRecord.objects.filter(
            amount__istartswith=search_str, owner=request.user
        ) | IncomeRecord.objects.filter(
            date__istartswith=search_str, owner=request.user
        ) | IncomeRecord.objects.filter(
            description__icontains=search_str, owner=request.user
        ) | IncomeRecord.objects.filter(
            source__icontains=search_str, owner=request.user
        )
        data = list(__income.values())
        return JsonResponse(data, safe=False)

class IncomeForm(forms.ModelForm):
    class Meta:
        model = IncomeRecord
        fields = ['amount', 'description', 'date', 'source']
        labels = {
            'date': 'Income Date'
        }

class IndexView(LoginRequiredMixin, ListView):
    model = IncomeRecord
    template_name = 'income/index.html'
    context_object_name = 'income'
    paginate_by = 5
    login_url = '/authentication/login'

    def get_queryset(self):
        # Filter the queryset by the logged-in user
        return IncomeRecord.objects.filter(owner=self.request.user).order_by('-date')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Add in the user's currency

        #add userpref

        '''
        user_preference = UserPreference.objects.filter(user=self.request.user).first()
        context['currency'] = user_preference.currency if user_preference else 'USD'  # Default to 'USD' if not set'''

        return context

class AddIncomeView(LoginRequiredMixin, FormView):
    template_name = 'income/add_income.html'
    form_class = IncomeForm
    success_url = reverse_lazy('income')  # Assuming 'income' is the name of the url for the income list view

    login_url = '/authentication/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = IncomeSource.objects.all()
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.instance.owner = self.request.user
        form.save()
        messages.success(self.request, 'Record saved successfully')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle invalid form submissions
        messages.error(self.request, 'Error saving form')
        return super().form_invalid(form)

class IncomeEditView(LoginRequiredMixin, UpdateView):
    model = IncomeRecord
    form_class = IncomeForm
    template_name = 'income/edit_income.html'
    success_url = reverse_lazy('income')  # Redirect to the income list view upon success

    login_url = '/authentication/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = IncomeSource.objects.all()  # Add the income sources to the context
        return context

    def form_valid(self, form):
        # Optionally, add any additional logic here before saving the form
        messages.success(self.request, 'Record updated successfully')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Optionally, handle the case where the form is invalid
        messages.error(self.request, 'Error updating the record')
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        """Ensure that the user can only edit their own income records."""
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise PermissionDenied  # Import PermissionDenied from django.core.exceptions
        return obj


class DeleteIncomeView(LoginRequiredMixin, View):
    login_url = '/authentication/login'
    # Assuming 'income' is the name of the URL to redirect to after deletion
    redirect_url = reverse_lazy('income')

    def get(self, request, *args, **kwargs):
        # Normally, deletion should be handled with POST request to ensure safety,
        # but if you're following the pattern from your original function:
        income_id = kwargs.get('id')
        income = IncomeRecord.objects.filter(pk=income_id, owner=request.user).first()
        if income:
            income.delete()
            messages.success(request, 'Record removed')
        else:
            messages.error(request, 'Record not found')
        return redirect(self.redirect_url)
