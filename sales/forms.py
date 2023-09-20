from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Div,Submit   
import datetime
from dateutil.relativedelta import relativedelta
from accounts.models import account_group


class create_sales_report(forms.Form):

    account_group =  forms.ModelChoiceField(widget=forms.Select, queryset=account_group.objects.filter(name__in=["Vendor","Customer","Dealers","Employee","Owner"]),required=False)
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'} ))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'} ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['start_date'].initial = datetime.date.today()
        self.fields['end_date'].initial = datetime.date.today()
        self.helper.layout = Layout(
             Div(
                    Div('account_group', css_class='col-md-4'),
                    Div('start_date', css_class='col-md-4'),
                    Div('end_date', css_class='col-md-4'),
                    css_class = 'row'
                ),
            )
        
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))