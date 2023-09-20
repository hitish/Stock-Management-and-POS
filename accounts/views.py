from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from accounts.forms import create_account_transaction_form,create_account_display_form
from .models import voucher,transaction,account,voucher_type
from datetime import datetime, timedelta
import core.utils as utils

from .filters import AccountFilter
from .tables import AccountTable

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.contrib.auth.mixins import UserPassesTestMixin

# Create your views here.

def create_account(request):
    print(request)


@user_passes_test(utils.is_accounts,login_url='/login/')
def account_transaction_view(request):
    context = {}
    context['form']= create_account_transaction_form()
   
    if request.method == 'POST':
        instance = request.POST
        #print(instance)
        amount = float(instance["amount"])
        if not instance['narration']:
            desc = None
        else:
            desc = instance['narration']

        vouch_type = voucher_type.objects.get(id=instance["voucher"])
        voucher_id = voucher.objects.create(voucher_type=vouch_type,amount=amount,description=desc)

        acc = account.objects.get(id=instance["selected_account"])
        pay_acc = account.objects.get(id=instance["payment_account"])

        if instance["transaction_type"] == "True":
            utils.create_transaction(voucher=voucher_id,acc=acc,entry_type=True,amount=amount)
            utils.create_transaction(voucher=voucher_id,acc=pay_acc,entry_type=True,amount=amount)
        else:
            utils.create_transaction(voucher=voucher_id,acc=acc,entry_type=False,amount=amount)
            utils.create_transaction(voucher=voucher_id,acc=pay_acc,entry_type=False,amount=amount)
        
    return render(request, "account_transactions.html", context)



@user_passes_test(utils.is_accounts,login_url='/login/')
def account_display_view(request):
    context = {}
    context['form']= create_account_display_form()
    #print(request)
    if request.method == 'POST':
        instance = request.POST
        acc = account.objects.get(id=instance["selected_account"])
        start_date = datetime.strptime(instance["start_date"], '%Y-%m-%d').date()
        end_date = datetime.strptime(instance["end_date"], '%Y-%m-%d').date() +timedelta(days=1)
        tran_table = []
        try:
            transactions = transaction.objects.filter(account_id = acc,timestamp__gte = start_date , timestamp__lte = end_date )
            
            for tran in transactions:
                tran_entry = {}
                tran_entry["date"] = tran.timestamp.date()
                tran_entry["description"] = tran.voucher.description
                if tran.entry_type:
                    tran_entry["debt"] = ""
                    tran_entry["credit"] = tran.amount
                else:
                    tran_entry["credit"] = ""
                    tran_entry["debt"] = tran.amount
                
                tran_entry["balance"] = tran.account_balance
                tran_table.append(tran_entry)

            context['form']= create_account_display_form(instance)
            context['tran_table']= tran_table
                
        except Exception as e:
            print(e)
    
    return render(request, "account_display.html", context)


class FilteredAccountListView(UserPassesTestMixin,SingleTableMixin, FilterView):
    login_url = "/login/"
    def test_func(self):
        return utils.is_accounts(self.request.user)
   
    table_class = AccountTable
   
    model = account
    template_name = "account_list.html"

    filterset_class = AccountFilter

    table_pagination = {
        "per_page": 20
    }