from django.contrib import admin
from .models import Bank, User

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_no', 'ifsc_code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('bank_name',)

admin.site.register(User)