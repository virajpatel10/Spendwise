from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Define the data models

class IncomeRecord(models.Model):
    amount = models.FloatField()  # Use FLOAT for decimal numbers
    date = models.DateField(default=now)  # Default date is the current date
    description = models.TextField()  # Detailed text description
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)  # Link to the User model
    source = models.CharField(max_length=266)  # Income source

    def __str__(self):
        return self.source  # String representation of the model

    class Meta:
        ordering = ['-date']  # Orders records by date in descending order


class IncomeSource(models.Model):
    name = models.CharField(max_length=255)  # Name of the income source

    def __str__(self):
        return self.name  # String representation of the model