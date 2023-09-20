from django import forms
from .models import account,voucher_type
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div,Submit   
import datetime
from dateutil.relativedelta import relativedelta
  
# create a ModelForm
class create_account_form(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = account
        fields = "__all__"


class create_account_transaction_form(forms.Form):
   
   voucher =  forms.ModelChoiceField(widget=forms.Select, queryset=voucher_type.objects.all())
   selected_account =  forms.ModelChoiceField(widget=forms.Select, queryset=account.objects.filter(~Q(group = 3 )))
   transaction_type = forms.ChoiceField(choices=[(True,"Payment Recieved"),(False,"Payment Done")])
   payment_account =  forms.ModelChoiceField(widget=forms.Select, queryset=account.objects.filter(group = 3 ))
   narration = forms.CharField(max_length=200)
   amount = forms.DecimalField(min_value=0.0)
  
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    


class create_account_display_form(forms.Form):

    selected_account =  forms.ModelChoiceField(widget=forms.Select, queryset=account.objects.all())
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'} ))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'} ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['start_date'].initial = datetime.date.today() -  relativedelta(days=7)
        self.fields['end_date'].initial = datetime.date.today()
        self.helper.layout = Layout(
             Div(
                    Div('selected_account', css_class='col-md-4'),
                    Div('start_date', css_class='col-md-4'),
                    Div('end_date', css_class='col-md-4'),
                    css_class = 'row'
                ),
            )
        
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))