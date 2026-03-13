from django.contrib import admin
from .models import Bank, User

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_no', 'ifsc_code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('bank_name',)

admin.site.register(User)

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.username