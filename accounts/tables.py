import django_tables2 as tables
from .models import account

    
class AccountTable(tables.Table):
   
    class Meta:
        model = account
        fields = ("id","name","phone_number","balance")
        