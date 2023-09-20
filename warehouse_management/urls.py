"""
URL configuration for warehouse_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from product.views import add_purchase_order_view,add_checked_stock_view,web_scrap_product_data,po_stock_check_view
from product.views import FilteredProductListView,reprint_barcode_view
from accounts.views import account_transaction_view,account_display_view,FilteredAccountListView
from sales.views import store_sale_view,sale_return_view,check_bill_view,sales_report
from django.views.generic.base import TemplateView


urlpatterns = [
    path('product/add-purchase-order/', add_purchase_order_view,name='add-purchase-order'),
    path('product/po-stock-checking/', po_stock_check_view,name='po-stock-checking'),
    path('product/add-checked-stock/', add_checked_stock_view, name='add-checked-stock'),
    path('product/stock-display/', FilteredProductListView.as_view() , name='stock-display'),
    path('product/reprint-barcode/', reprint_barcode_view , name='reprint-barcode'),


    path('sales/store-sale/', store_sale_view, name='store-sale'),
    path('sales/sale-return/', sale_return_view, name='sale-return'),
    path('sales/check-bill-details/', check_bill_view, name='check-bill-details'),
    path('sales/sales-report/', sales_report, name='sales-report'),


    path('product/add-checked-stock/<str:product_id>', web_scrap_product_data),
    path('accounts/account-transaction/', account_transaction_view, name='account-transaction'),
    path('accounts/account-display/', account_display_view, name='account-display'),
    path('accounts/account-list/', FilteredAccountListView.as_view() , name='account-list'),
    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('', include('django.contrib.auth.urls')),
]
