from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render,redirect
from django.template.loader import get_template
from product.forms import Purchase_order_form,po_stock_check_form
from .models import Purchase_order,unchecked_stock,checked_stock,Product_brand,Product_categories,product_qc_status,Product_details
from .filters import ProductFilter
from .tables import ProductTable
import pandas as pd
import math
from django.core.files.storage import FileSystemStorage
import core.utils as utils
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.contrib.auth.mixins import UserPassesTestMixin
import os
from django.conf import settings



@user_passes_test(utils.is_stock_manager,login_url='/login/')
def add_purchase_order_view(request):
    context={}
    form = Purchase_order_form()
    if request.method == 'POST' and request.FILES['order_detail_file']:
        instance = request.POST
        po_added = Purchase_order.objects.create(purchase_details=instance['purchase_details'],order_detail_file=request.FILES['order_detail_file'],quantity=instance['quantity'],value=instance['value'])
        
        if po_added:
            myfile = request.FILES['order_detail_file']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)              
            exceldata = pd.read_excel(filename,engine="openpyxl")         
            dbframe = exceldata
            i=0
            product= {}
            for df in dbframe.iterrows():
                
                row = changeNaNtoNone(dbframe,i) 
                
                if not row['online_code']:
                    product_code = utils.create_product_code(row)
                else:
                    product_code = row['online_code']

                product = utils.check_product(product_code)

                if not product:
                    product = utils.add_product(row,product_code)
                
                utils.update_product_unchecked_stock(product_code,row['quantity'])                

                box_no = row['box_id']
                if box_no:
                    try:
                       float(box_no)
                       box_no = math.trunc(float(box_no)) 
                    except ValueError:
                        pass

                    box_no = str(box_no)

                obj = unchecked_stock.objects.create(purchase_id=po_added,box_id=box_no, online_code=product,
                                            quantity=row['quantity'], sosp=row['sosp'])           
                obj.save()
                i = i + 1
            form = Purchase_order_form()
        else:
            form = Purchase_order_form(instance)
    
    
    context["form"] = form
    
    return render(request, "add_purchase_order.html",context )



@user_passes_test(utils.is_stock_manager,login_url='/login/')
def add_checked_stock_view(request):
    context = {}
    context['brands']= Product_brand.objects.all()
    context['categories']= Product_categories.objects.all()
    context['qc_status_list'] = product_qc_status.objects.all()
    context["product_saved"] = 0
    
    if request.method == 'POST':
        instance = request.POST
        if not instance['online_code']:
            product_code = utils.create_product_code(instance)
        else:
            product_code = instance['online_code']

        product = utils.check_product(product_code)
        if not product:
            product = utils.add_product(instance,product_code)
        else:
            product = utils.update_product_details(instance,product)

        qc_status = product_qc_status.objects.get(id=instance['qc_status'])
        
        if utils.is_null(instance['cosp']) or instance['cosp'] == "":
            cosp = None
        else:
            cosp = instance['cosp']  

        

        obj = checked_stock.objects.create(product_id=product,quantity=instance['quantity'], cosp=cosp,mbp=instance['mbp'],qc_status=qc_status)    
        
        if obj:
            try:
                utils.update_product_checked_stock(product_code,instance['quantity'])
                code = utils.create_barcode(qc_status.qc_code,obj.id)
                #print(code)
                obj.barcode = code
                obj.save()
                utils.generate_barcode_file(code)
                context["product_saved"] = obj
                context["product_name"] = product.product_name

                if product.mrp == None:
                        mrp = "NA"
                else:
                        mrp = int(float(product.mrp))

                context["mrp"] = mrp
                
                context["message"] = "Product Saved Successfully"
            except Exception as e:
                error = 'Error updating stock {}'.format(e)
                print(error)
                context["message"] = error
                context["product_saved"] = False
              
        
        
    else:
        context["message"] = "Product Not Saved"
        context["product_saved"] = False
        


    #tmpl = get_template("add_checked_stock.html")
    #tmpl_string = tmpl.render({"form": form})
    
    #    return HttpResponse(tmpl_string)
    return render(request, "add_checked_stock.html", context)


def changeNaNtoNone(dbframe,row):
    returnrow = {}
    colm = list(dbframe)
            
    for x in colm:
        if dbframe[x][row] != dbframe[x][row]:
            returnrow[x] = None
        else:
            returnrow[x] = dbframe[x][row]
    return returnrow

async def web_scrap_product_data(response,product_id):
   # print(product_id)
    length = len(product_id)
    if length == 10:
        link = 'https://www.amazon.in/dp/{}'.format(product_id)
        result = await utils.getAmazonProductDetails(link)
    elif length==16:
        link = 'https://www.flipkart.com/product/p/item?pid={}&marketplace=FLIPKART&sattr[]=color&sattr[]=size&st=size'.format(product_id)
        result =await utils.getFlipkartProductDetails(link)
    elif length==14:
        result = {}
    else:
        return "Code not Valid"
    # return json for the js caller
    product = await utils.sync_check_product(product_id)
       
    if product:
        if 'model' in result.keys():
            if result["model"] == "" and not product.model == None:
                result["model"] = product.model
        else:
            result["model"] = product.model
        
        if 'color' in result.keys():
            if result["color"] == "" and not product.color == None:
                result["color"] = product.color
        else:
            result["color"] = product.color

        if 'size' in result.keys():
          if result["size"] == "" and not product.size == None:
            result["size"] = product.size
        else:
            result["size"] = product.size

        if 'rating' in result.keys():
          if result["rating"] == "" and not product.rating == None:
            result["rating"] = product.rating
        else:
            result["rating"] = product.rating

        if 'mrp' in result.keys():

            if result["mrp"] == "" and not product.mrp == None:
                result["mrp"] = product.mrp
            elif not result["mrp"] == "" and not product.mrp == None:
                if product.mrp > float(result["mrp"]):
                    result["mrp"] = product.mrp
        else:
            result["mrp"] = product.mrp


    return JsonResponse(result, content_type="application/json")


@user_passes_test(utils.is_stock_manager,login_url='/login/')
def po_stock_check_view(request):
    context = {}
    context['brands']= Product_brand.objects.all()
    context['categories']= Product_categories.objects.all()
    context['qc_status_list'] = product_qc_status.objects.all()
    context['products'] = {}
    context["product_saved"] = False
    form_purchase_order = po_stock_check_form()
   
    if request.method == 'GET':
        instance = request.GET
        if 'Purchase_order' in instance.keys():
            products = utils.get_products_po(instance["Purchase_order"],instance["Box_no"])
            context['products'] = products
            form_purchase_order = po_stock_check_form(instance)
            
    if request.method == 'POST':
        instance = request.POST
        form_purchase_order = po_stock_check_form()
        
        product = utils.check_product(instance['online_code'])

        product = utils.update_product_details(instance,product)

        qc_status = product_qc_status.objects.get(id=instance['qc_status'])
        
        if utils.is_null(instance['cosp']) or instance['cosp'] == "":
            cosp = None
        else:
            cosp = instance['cosp']

        qty = int(instance['quantity'])
        
        if qty > 0 :
            obj = checked_stock.objects.create(product_id=product,quantity=qty, cosp=cosp,mbp=instance['mbp'],qc_status=qc_status)

            if obj:
                try:
                    utils.update_product_stock_cheking(instance['unchecked_id'],qty,True)
                    code = utils.create_barcode(qc_status.qc_code,obj.id)
                    obj.barcode = code
                    obj.save()
                    utils.generate_barcode_file(code)
                    
                    context["product_saved"] = obj
                    context["product_name"] = product.product_name
                    
                    if product.mrp == None:
                        mrp = "NA"
                    else:
                        mrp = int(float(product.mrp))

                    context["mrp"] = mrp
                    context["message"] = "Product Saved Successfully"

                    get_instance = request.GET
                    if 'Purchase_order' in get_instance.keys():
                        products = utils.get_products_po(get_instance["Purchase_order"],get_instance["Box_no"])
                        context['products'] = products
                        form_purchase_order = po_stock_check_form(get_instance)
      

                except Exception as e:
                    error = 'Error updating stock {}'.format(e)
                    print(error)
                    context["message"] = error
                    context["product_saved"] = False
        else:
            context["message"] = "Quantity cannot be zero"
            context["product_saved"] = False

        


    context['form_purchase_order']  = form_purchase_order

    return render(request, "po_stock_check.html", context=context)



class FilteredProductListView(UserPassesTestMixin,SingleTableMixin, FilterView):
    login_url = "/login/"
    def test_func(self):
        return utils.is_stock_manager(self.request.user)
   
    table_class = ProductTable
   
    model = Product_details
    template_name = "stock_display.html"

    filterset_class = ProductFilter

    table_pagination = {
        "per_page": 20
    }


@user_passes_test(utils.is_stock_manager,login_url='/login/')
def reprint_barcode_view(request):
    context = {}
   
    if request.method == 'GET':
        instance = request.GET
        if 'barcode' in instance.keys():
            barcode = instance["barcode"]
            checked_product = checked_stock.objects.get(barcode=barcode)
            if checked_product:
                path = os.path.join(settings.BASE_DIR, "static/barcode/"+barcode+".svg")
                if not os.path.isfile(path):
                    utils.generate_barcode_file(barcode)
                context["product_saved"] = checked_product
                context["product_name"] = checked_product.product_id.product_name
                context["mrp"] = int(float(checked_product.product_id.mrp))
                context["message"] = ""
                context["barcode"]=barcode

    return render(request, "reprint_barcode.html", context=context)