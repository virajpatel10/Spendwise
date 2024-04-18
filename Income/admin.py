from django.contrib import admin
from .models import IncomeRecord, IncomeSource
# Register your models here.

admin.site.register(IncomeRecord)
admin.site.register(IncomeSource)
