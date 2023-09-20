import django_filters
from .models import account

class AccountFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    balance__gt = django_filters.NumberFilter(field_name='balance', lookup_expr='gt')
    balance__lt = django_filters.NumberFilter(field_name='balance', lookup_expr='lt')
    
    class Meta:
        model = account
        fields = ['name', 'phone_number', 'group',]