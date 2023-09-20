import django_tables2 as tables
from .models import Product_details

    
class ProductTable(tables.Table):
    product_id = tables.Column()
    class Meta:
        model = Product_details
        fields = ("product_id","product_name","product_stock__checked_stock","product_stock__unchecked_stock")
        
        
    
    def render_product_id(self, value):
        return f"{value}"
   