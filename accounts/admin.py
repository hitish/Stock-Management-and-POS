from django.contrib import admin

# Register your models here.
from .models import account,voucher_type,account_group


admin.site.register(account)
admin.site.register(account_group)
admin.site.register(voucher_type)