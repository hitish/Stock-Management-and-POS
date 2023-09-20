from django.db import models
from accounts.models import account
from address.models import Address

# Create your models here.
class Product_details(models.Model):
   product_id = models.CharField(max_length=100,primary_key=True )
   product_name = models.CharField(max_length=300,null=True)
   category_id =  models.ForeignKey("Product_categories",on_delete=models.CASCADE,null=True)
   brand_id = models.ForeignKey("Product_brand",on_delete=models.CASCADE,null=True)
   rating = models.FloatField(null=True)
   mrp = models.FloatField(null=True)
   color = models.CharField(max_length=100,null=True) 
   model = models.CharField(max_length=10,null=True) 
   size = models.CharField(max_length=50,null=True)
   metadata = models.JSONField(null=True)
   timestamp = models.DateTimeField(auto_now_add=True)

   def __str__(self):
        return self.product_name


class Product_categories(models.Model):
    category_name= models.CharField(max_length=100,unique=True)
    category_desc=models.TextField(null=True)
    parent_category_id = models.ForeignKey("Product_categories",on_delete=models.CASCADE,null=True,related_name="parent_category")

    def __str__(self):
        return self.category_name


class Product_brand(models.Model):
    brand_name= models.CharField(max_length=100,unique=True)
    brand_desc=models.TextField(null=True)

    def __str__(self):
        return self.brand_name

class Purchase_order(models.Model):
    purchase_details= models.CharField(max_length=100)
    order_detail_file = models.FileField(upload_to='purchase_file/',null=True)
    value=models.BigIntegerField(null=True)
    quantity = models.BigIntegerField(null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.purchase_details


class product_stock(models.Model):
    product_id = models.OneToOneField("Product_details", on_delete=models.CASCADE)
    checked_stock = models.IntegerField(null=True,default=0)
    unchecked_stock = models.IntegerField(null=True,default=0)

class unchecked_stock(models.Model):
    purchase_id = models.ForeignKey("Purchase_order",on_delete=models.CASCADE)
    box_id = models.CharField( max_length=100,null=True)
    online_code = models.ForeignKey("Product_details", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    checked_quantity = models.IntegerField(null=True,default=0)
    sosp = models.FloatField(null=True)
    #cosp = models.FloatField(null = True)
    timestamp = models.DateTimeField(auto_now_add=True)

class checked_stock(models.Model):
    product_id = models.ForeignKey("Product_details", on_delete=models.CASCADE)
    purchase_id = models.ForeignKey("Purchase_order",on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField()
    sold_quantity = models.IntegerField(null=True,default=0)
    sosp = models.FloatField(null=True)
    cosp = models.FloatField(null=True)
    mbp = models.FloatField()
    qc_status = models.ForeignKey("product_qc_status", on_delete=models.CASCADE,null=True)
    barcode = models.CharField(max_length=12,default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

class product_qc_status(models.Model):
    qc_status = models.CharField(max_length=100,unique=True)
    qc_details = models.TextField(null=True)
    qc_code = models.CharField(max_length=3,default='FRH')

