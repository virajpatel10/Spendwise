from django.contrib import admin
from .models import IncomeRecord, IncomeSource
# Register your models here.

admin.site.register(IncomeSource)
admin.site.register(IncomeRecord)
