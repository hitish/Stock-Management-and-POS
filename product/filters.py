import django_filters
from .models import Product_details

class ProductFilter(django_filters.FilterSet):
    product_name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Product_details
        fields = ['product_name', 'category_id', 'brand_id']