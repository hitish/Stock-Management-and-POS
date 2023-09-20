from django.db import models
from accounts.models import account
from product.models import checked_stock
from address.models import Address

# Create your models here.
class sale_bill(models.Model):
    account_id = models.ForeignKey("accounts.account", on_delete=models.CASCADE,null=True)
    address_id = models.ForeignKey("address.Address", on_delete=models.CASCADE,null=True)
    bill_amount = models.DecimalField(decimal_places=2,max_digits=25)
    product_qty = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

class product_sold(models.Model):
    sale_bill_id = models.ForeignKey("sale_bill", on_delete=models.CASCADE,null=True)
    checked_stock_id = models.ForeignKey("product.checked_stock", on_delete=models.CASCADE,null=True)
    qty = models.IntegerField()
    discount = models.DecimalField(default=0,decimal_places=2,max_digits=5)
    price_per_piece = models.DecimalField(decimal_places=2,max_digits=25)


class product_returned(models.Model):
    sale_bill_id = models.ForeignKey("sale_bill", on_delete=models.CASCADE,null=True)
    product = models.ForeignKey("product.product_details", on_delete=models.CASCADE,null=True)
    qty = models.IntegerField()
    price_per_piece = models.DecimalField(decimal_places=2,max_digits=25)
    reason = models.CharField(null=True,max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)