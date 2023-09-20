from django.db import models
from address.models import AddressField
from django.core.validators import RegexValidator


class account(models.Model):
    name = models.CharField(max_length=150,unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # Validators should be a list
    group = models.ForeignKey("account_group",on_delete=models.CASCADE)
    parent_account = models.ForeignKey("account",on_delete=models.CASCADE,null=True,blank=True)
    balance = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class account_details(models.Model):
    account_id = models.OneToOneField("account",primary_key=True,on_delete=models.CASCADE)
    address = AddressField(related_name='+', blank=True, null=True)

    
class account_group(models.Model):
    name = models.CharField(max_length=150)
    purpose = models.TextField(null=True)

    def __str__(self):
        return self.name

class voucher_type(models.Model):
    name = models.CharField(max_length=150) #1)journal 2)sales 3)expenses 4)return 5)bill_payments
    desc = models.TextField(null=True)

    def __str__(self):
        return self.name


class voucher(models.Model):
    voucher_type = models.ForeignKey("voucher_type",on_delete=models.CASCADE)
    voucher_object_id = models.CharField(max_length=100)
    description = models.TextField(null=True)
    amount = models.DecimalField(decimal_places=2,max_digits=25)
    timestamp = models.DateTimeField(auto_now_add=True)


class transaction(models.Model):
    voucher = models.ForeignKey("voucher",on_delete=models.CASCADE)
    account_id = models.ForeignKey("account",on_delete=models.CASCADE)
    entry_type = models.BooleanField(null=False) # 0 for debt and 1 for credit
    amount = models.DecimalField(decimal_places=2,max_digits=25)
    account_balance = models.FloatField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

