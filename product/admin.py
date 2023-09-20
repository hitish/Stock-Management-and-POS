from typing import Any
from django.contrib import admin

# Register your models here.
from .models import Product_brand,Purchase_order,Product_categories,Product_details,unchecked_stock,product_qc_status



class poAdmin(admin.ModelAdmin):
    list_display = ["purchase_details", "quantity", "value"]
    
    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        
        return super().save_model(request, obj, form, change)
        
       


admin.site.register(Product_brand)
admin.site.register(Product_details)
admin.site.register(Product_categories)
admin.site.register(unchecked_stock)
admin.site.register(product_qc_status)
admin.site.register(Purchase_order,poAdmin)