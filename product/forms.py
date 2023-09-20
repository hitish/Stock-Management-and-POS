# import form class from django
from django import forms
from .models import Purchase_order,checked_stock
from accounts.models import account
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div,Submit 
from core.fields import ListTextWidget 
from django.forms import formset_factory
  
# create a ModelForm
class Purchase_order_form(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Purchase_order
        fields = "__all__"


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        

        
class po_stock_check_form(forms.Form):
    Purchase_order = forms.ModelChoiceField(queryset=Purchase_order.objects.all())
    Box_no = forms.CharField( max_length=100, required=False)



class sales_form(forms.Form):
    selected_account =  forms.CharField(required=True, widget= ListTextWidget(data_list=[(account1.name) for account1 in account.objects.filter(~Q(group = 3 ))],name="account_list"))
    Phone_number = forms.IntegerField(  max_value=9999999999,min_value=1000000000)
    address = forms.CharField(max_length=300)
   

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
                Div(
                    Div('selected_account', css_class='col-md-4'),
                    Div('Phone_number', css_class='col-md-4'),
                    css_class = 'row'
                ),
                Div('address', css_class='col-md-12'),
                #Div(
                #    Div('product', css_class='col-md-6'),
                #    Div('quantity', css_class='col-md-2'),
                #    Div('price_per_pc', css_class='col-md-2'),
                #    Div('row_total', css_class='col-md-2'),
                #    css_class = 'row'
                #),
            )
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))



class product_row_form(forms.Form):

    product = forms.CharField(required=True, widget= ListTextWidget(data_list=[(product1.product_id) for product1 in checked_stock.objects.filter(quantity = 3 )],name="product_list"))
    quantity    = forms.IntegerField(min_value=1)
    price_per_pc = forms.DecimalField()
    row_total = forms.DecimalField()


product_row_formset = formset_factory(product_row_form, extra=1)