from django.shortcuts import render
from django.db.models import Q,F
from django.contrib.auth.decorators import user_passes_test
from .models import sale_bill,product_sold,product_returned
from accounts.models import account,voucher,transaction,voucher_type,account_group
from product.models import checked_stock,product_stock,Product_details,product_qc_status
import core.utils as utils
from datetime import datetime, timedelta

from .forms import create_sales_report

# Create your views here.

@user_passes_test(utils.is_sales,login_url='/login/')
def store_sale_view(request):
    context = {}
    context['checked_stock'] = checked_stock.objects.filter(quantity__gt = F("sold_quantity"))
    criterion1 = ~Q(group = 3)
    context['accounts'] = account.objects.filter( Q(is_active=True) & criterion1)
    criterion2 = Q(group = 3)
    context['pay_accounts'] = account.objects.filter( Q(is_active=True) & criterion2)
    context['success'] = False
    
    context["total_bill"]=0

    if request.method == 'POST':
        instance = request.POST
        product_count = int(instance["product_count"])
        prod_sold = []
        products = []
        total_qty = 0
        total_bill = 0
        
        #print(instance)
        if not instance['account_id']:
            account_id = utils.create_account(instance['account_name'],instance['phone'],instance['address'])
        else:
            account_id = account.objects.get(id=instance['account_id'])

        context["account"] = account_id

        #checking loop
        for count in range(int(instance["product_count"])):
            item_num = str(count)
            product = instance["selected_product"+ item_num]
            qty = int(instance["qty"+ item_num])
            total_qty += qty
            priceperpiece = float(instance["priceperpiece"+ item_num])
            total_bill += qty * priceperpiece
            checked_Stock_element = checked_stock.objects.get(id=product) 
            prod_sold.append([checked_Stock_element,qty,priceperpiece])
            prod_name = checked_Stock_element.product_id.product_name
            prod_total = qty * priceperpiece
            products.append([prod_name,qty,int(priceperpiece),int(prod_total)])
        
        context["products"] = products
        context["total_qty"] = total_qty
        context["total_bill"] = int(total_bill)

        if product_count > 0:
            bill_id = sale_bill.objects.create(account_id=account_id,bill_amount=total_bill,product_qty=total_qty)
            context["number"] = bill_id.id

        if bill_id:
            for prod in prod_sold:
                #reduce stock at checked stock, product_Stock and product sold
                checked_Stock_ele = prod[0]  
                product_sold.objects.create(sale_bill_id=bill_id,checked_stock_id=checked_Stock_ele,qty=prod[1],price_per_piece=prod[2])
                checked_Stock_ele.sold_quantity = checked_Stock_ele.sold_quantity + prod[1]
                checked_Stock_ele.save()

                product_stock_ele = product_stock.objects.get(product_id = checked_Stock_ele.product_id)
                product_stock_ele.checked_stock = product_stock_ele.checked_stock - prod[1]
                product_stock_ele.save()

            voucher__type = voucher_type.objects.get(id=2)
            desc = "Sales transaction for id " + str(bill_id.id) + " " + instance["reference-detail"]
            voucher_id = voucher.objects.create(voucher_type=voucher__type,voucher_object_id=bill_id.id,description=desc,amount=total_bill)

            if voucher_id:
                utils.create_transaction(voucher=voucher_id,acc=account_id,entry_type=False,amount=total_bill)


                if not instance["payment-option"] == "-2":
                    paid_amount= float(instance["amount_paid"])
                    pay_voucher__type = voucher_type.objects.get(id=5)
                    pay_voucher_id = voucher.objects.create(voucher_type=pay_voucher__type,voucher_object_id=bill_id.id,description=desc,amount=paid_amount)
                  
                    if pay_voucher_id:
                        utils.create_transaction(voucher=pay_voucher_id,acc=account_id,entry_type=True,amount=paid_amount)
                        pay_acc_id = account.objects.get(id = instance["payment-option"])
                        utils.create_transaction(voucher=pay_voucher_id,acc=pay_acc_id,entry_type=True,amount=paid_amount)
                        context['success'] = True
                    

         
    return render(request, "store_sale.html", context=context)

@user_passes_test(utils.is_sales,login_url='/login/')
def sale_return_view(request):
    context = {}
    context['qc_status_list'] = product_qc_status.objects.all()
    criterion2 = Q(group = 3)
    context['pay_accounts'] = account.objects.filter( Q(is_active=True) & criterion2)
    context['success'] = False
    context["product_saved"] = False
    if request.method == 'GET':
        instance = request.GET
        if "sales_id" in instance.keys():
             product_list = product_sold.objects.filter(sale_bill_id=instance["sales_id"])
             products = []
             for prod in product_list:
                 
                  product = prod.checked_stock_id.product_id
                  stock_objs = product_returned.objects.filter(sale_bill_id=instance["sales_id"],product=product)
                  returned_qty = 0
                  for stock_obj in stock_objs:
                      returned_qty += stock_obj.qty

                  if returned_qty > 0:
                    qty = prod.qty - returned_qty 
                  else: 
                    qty = prod.qty  
                  ppp = prod.price_per_piece
                  if qty > 0:
                    products.append([product,qty,ppp])
             
             context["products"] = products
             context["sales_id"] = instance["sales_id"]

    
    if request.method == 'POST':
        instance = request.POST
        product_code = instance['return-product']
        sales_id = instance['sales_id']
        sales_obj = sale_bill.objects.get(id=sales_id)
        product = Product_details.objects.get(product_id=product_code)
        qc_status = product_qc_status.objects.get(id=instance['qc_status'])
        account_id = sales_obj.account_id
        amount_refunded = float(instance["amount_refunded"])
        return_qty = int(instance['return_qty'])
        #add products to return table

        product_returned.objects.create(sale_bill_id=sales_obj,product=product,qty=return_qty,price_per_piece=instance['ppp'],reason =instance["return_desc"] )

        obj = checked_stock.objects.create(product_id=product,quantity=return_qty,mbp=instance['amount_new_mbp'],qc_status=qc_status)    
        
        if obj:
            try:
                prod_stock = product_stock.objects.get(product_id=product)
                prod_stock.checked_stock = prod_stock.checked_stock + return_qty
                prod_stock.save()
                code = utils.create_barcode(qc_status.qc_code,obj.id)
                obj.barcode = code
                obj.save()
                utils.generate_barcode_file(code)
                context["product_saved"] = obj
                context["product_name"] = product.product_name
                context["mrp"] = int(float(product.mrp))
                context["message"] = "Product Saved Successfully"
            except Exception as e:
                error = 'Error updating stock {}'.format(e)
                print(error)
                context["message"] = error
                context["product_saved"] = False

     
        else:
            context["message"] = "Product Not Saved"
            context["product_saved"] = False

        #transaction for return
        voucher__type = voucher_type.objects.get(id=4)
        desc = "Return transaction for id " + str(sales_id) + " " + instance["return_desc"]
        voucher_id = voucher.objects.create(voucher_type=voucher__type,voucher_object_id=sales_obj,description=desc,amount=amount_refunded)
        if voucher_id:
                utils.create_transaction(voucher=voucher_id,acc=account_id,entry_type=True,amount=amount_refunded)
                if not instance["payment-option"] == "-2":
                    
                    pay_voucher__type = voucher_type.objects.get(id=5)
                    pay_voucher_id = voucher.objects.create(voucher_type=pay_voucher__type,voucher_object_id=sales_obj,description=desc,amount=amount_refunded)
                  
                    if pay_voucher_id:
                        utils.create_transaction(voucher=pay_voucher_id,acc=account_id,entry_type=False,amount=amount_refunded)

                        pay_acc_id = account.objects.get(id = instance["payment-option"])
                        
                        utils.create_transaction(voucher=pay_voucher_id,acc=pay_acc_id,entry_type=False,amount=amount_refunded)
    return render(request, "sale_return.html", context=context)
    


@user_passes_test(utils.is_sales,login_url='/login/')
def check_bill_view(request):
    context = {}
    if request.method == 'GET':
        instance = request.GET

        if "sales_id" in instance.keys():
             
             sales_id = instance["sales_id"]
             sales_obj = sale_bill.objects.get(id = sales_id)
             if sales_obj:
                account_details = account.objects.get(id=sales_obj.account_id.id)
                context["account"] = account_details
                context["date"] = sales_obj.timestamp
                context["item_total"] = sales_obj.product_qty
                context["grand_total"] = int(sales_obj.bill_amount)

                product_list = product_sold.objects.filter(sale_bill_id=instance["sales_id"])

                products = []
                for prod in product_list:
                    
                    product_name = prod.checked_stock_id.product_id.product_name
                    qty = prod.qty  
                    ppp = prod.price_per_piece
                    product_total = qty * ppp
                    
                    products.append([product_name,qty,int(ppp),int(product_total)])
                
                context["products"] = products
                context["sales_id"] = instance["sales_id"]
                
    return render(request, "check_bill_details.html", context=context)



@user_passes_test(utils.is_sales,login_url='/login/')
def sales_report(request):
    context = {}
    context["form"] = create_sales_report()

    if request.method == 'POST':
        instance = request.POST
        if not instance["account_group"] == '' :
            acc_type = account_group.objects.get(id=instance["account_group"])
        else:
            acc_type = "all"

        start_date = datetime.strptime(instance["start_date"], '%Y-%m-%d').date()
        end_date = datetime.strptime(instance["end_date"], '%Y-%m-%d').date() +timedelta(days=1)
        sales_table = []
        try:
            voucher__type = voucher_type.objects.get(id=2)
            sales = voucher.objects.filter(voucher_type = voucher__type,timestamp__gte = start_date , timestamp__lte = end_date )
            
          
            for sale in sales:
                sale_entry = {}
                sale_entry["date"] = sale.timestamp.date()  
                sale_entry["description"] = sale.description
                str1 = sale.voucher_object_id
                sale_voucher = sale_bill.objects.get(id=str1)
                
                if sale_voucher:
                    sale_entry["account_id"] = sale_voucher.account_id.id
                    sale_entry["name"] = sale_voucher.account_id.name
                
                sale_entry["amount"] = sale.amount

                if acc_type == "all":
                    sales_table.append(sale_entry)
                    
                elif acc_type == sale_voucher.account_id.group:
                    sales_table.append(sale_entry)
                    

            context['form']= create_sales_report(instance)
            context['sales_table']= sales_table
                
        except Exception as e:
            print(e)

    return render(request, "sales_report.html", context=context)