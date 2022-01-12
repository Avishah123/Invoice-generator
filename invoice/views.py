from django.forms.models import ModelForm, modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.template.loader import get_template
from django.http import HttpResponse
from django.views import View
from .models import LineItem, Invoice
from .forms import LineItemFormset, InvoiceForm, Product_update_form, AuthorBooksFormset, OrderForm
from django.views import generic
import pdfkit
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, CreateView, DetailView, FormView)

from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory


class InvoiceListView(View):
    def get(self, *args, **kwargs):
        invoices = Invoice.objects.all()
        context = {
            "invoices": invoices,
        }

        return render(self.request, 'invoice/invoice-list.html', context)

    def post(self, request):
        # import pdb;pdb.set_trace()
        invoice_ids = request.POST.getlist("invoice_id")
        invoice_ids = list(map(int, invoice_ids))

        update_status_for_invoices = int(request.POST['status'])
        invoices = Invoice.objects.filter(id__in=invoice_ids)
        # import pdb;pdb.set_trace()
        if update_status_for_invoices == 0:
            invoices.update(status=False)
        else:
            invoices.update(status=True)

        return redirect('invoice:invoice-list')


class invoiceupdate(generic.UpdateView):
    model = Invoice
    template_name = 'invoice/test.html'
    fields = ['customer_email', 'billing_address', 'message']
    success_url = reverse_lazy('invoice:invoice-list')


class productupdate(generic.UpdateView):
    model = LineItem
    template_name = 'invoice/test.html'
    fields = ['customer', 'service', 'description',
        'quantity', 'rate', 'amount']

    success_url = reverse_lazy('invoice:invoice-list')


def createInvoice(request):
    """
    Invoice Generator page it will have Functionality to create new invoices,
    this will be protected view, only admin has the authority to read and make
    changes here.
    """

    heading_message = 'Formset Demo'
    if request.method == 'GET':
        formset = LineItemFormset(request.GET or None)
        form = InvoiceForm(request.GET or None)
    elif request.method == 'POST':
        formset = LineItemFormset(request.POST)
        form = InvoiceForm(request.POST)

        # invoice = Invoice.objects.create(customer=form.data["customer"],
        #             customer_email=form.data["customer_email"],
        #             billing_address = form.data["billing_address"],
        #             date=form.data["date"],
        #             due_date=form.data["due_date"],
        #             message=form.data["message"],
        #             )
        if form.is_valid():
            invoice = Invoice.objects.create(customer=form.data["customer"],
                    customer_email=form.data["customer_email"],
                    billing_address=form.data["billing_address"],
                    date=form.data["date"],
                    due_date=form.data["due_date"],
                    message=form.data["message"],
                    )
            # invoice.save()

        if formset.is_valid():
            # import pdb;pdb.set_trace()
            # extract name and other data from each form and save
            total = 0
            for form in formset:
                service = form.cleaned_data.get('service')
                description = form.cleaned_data.get('description')
                quantity = form.cleaned_data.get('quantity')
                rate = form.cleaned_data.get('rate')
                if service and description and quantity and rate:
                    amount = float(rate)*float(quantity)
                    total += amount
                    LineItem(customer=invoice,
                            service=service,
                            description=description,
                            quantity=quantity,
                            rate=rate,
                            amount=amount).save()
            invoice.total_amount = total
            invoice.save()
            try:
                generate_PDF(request, id=invoice.id)
            except Exception as e:
                print(f"********{e}********")
            return redirect('/')
    context = {
        "title": "Invoice Generator",
        "formset": formset,
        "form": form,
        # "customer" : Invoice.objects.values('customer'),
    }
    return render(request, 'invoice/invoice-create.html', context)


def view_PDF(request, id=None):
    invoice = get_object_or_404(Invoice, id=id)
    lineitem = invoice.lineitem_set.all()

    context = {
        "company": {
            "name": "AviTech ",
            "address": "xyz lane , Mumbai ",
            "phone": "(916) XXX XXXX",
            "email": "contact@avitech.com",
        },
        "invoice_id": invoice.id,
        "invoice_total": invoice.total_amount,
        "customer": invoice.customer,
        "customer_email": invoice.customer_email,
        "date": invoice.date,
        "due_date": invoice.due_date,
        "billing_address": invoice.billing_address,
        "message": invoice.message,
        "lineitem": lineitem,

    }
    return render(request, 'invoice/pdf_template.html', context)


def generate_PDF(request, id):
    # Use False instead of output path to save pdf to a variable
    pdf = pdfkit.from_url(request.build_absolute_uri(reverse('invoice:invoice-detail', args=[id])), False)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    return response


def change_status(request):
    return redirect('invoice:invoice-list')


def view_404(request,  *args, **kwargs):

    return redirect('invoice:invoice-list')


def product_view(request, customer):
    invoice = LineItem.objects.filter(
        customer=Invoice.objects.get(customer=customer))
    # invoice= LineItem.objects.all()
    for inst in invoice:
        print(inst.id)

    return render(request, 'invoice/test2.html', {'invoice': invoice})


def edit_product(request, customer):
    template = 'invoice/test3.html'
    book = get_object_or_404(
        LineItem, customer=Invoice.objects.get(customer=customer))
    form = Product_update_form(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect('/')
    context = {"form": form}
    return render(request, 'invoice/test.html', context)


def updateOrder(request, customer):
    order = LineItem.objects.filter(
        customer=Invoice.objects.get(customer=customer))
    print(order)
    array = []
    for i in order:
        print(i.id)

        form = OrderForm(instance=(i))
        array.append(form)

        if request.method == 'POST':
            form = OrderForm(request.POST, instance=i)

            if form.is_valid():
                form.save()

    print(array)
    context = {'form': array}

    return render(request, 'invoice/order_form.html', context)

    # return redirect('/')



    


def createOrder(request, customer):
    OrderFormSet = modelformset_factory(LineItem, fields=('rate', 'description'),extra=0)

    formset = OrderFormSet(queryset=LineItem.objects.filter(
        customer=Invoice.objects.get(customer=customer)))

    
    
    for form in formset:
        print(form)
    
    
    
    
    query1 = queryset=LineItem.objects.filter(
        customer=Invoice.objects.get(customer=customer))
    
    
    for i in query1:
        print(i.amount)
        
        
    # form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':

        # print('Printing POST:', request.POST)
       
        # form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST)

        if formset.is_valid():
            
            formset.save()
            sum1=0
            query2 = queryset=LineItem.objects.filter(customer=Invoice.objects.get(customer=customer))
            for i in query2:
                sum1 += i.amount
                print(sum1)
            invoice = Invoice.objects.get(customer=customer)
            invoice.total_amount = sum1
            invoice.save()
                


            
        
            # new_func(query1)            
            return redirect('/')
        
        

           
        

    context = {'formset':formset}
    
    return render(request, 'invoice/order_form.html',{'formset':formset})






# class AuthorProductEditView(SingleObjectMixin, FormView):

#     pass

    # model = LineItem
    # # pk_url_kwarg = "customer"
    # # customer_url_kwarg = 'customer'
    # query_pk_and_slug = True
    # template_name = 'invoice/author_books_edit.html'

    # # customer = self.kwargs['customer']

    # # def get_queryset(self):
    # #     self.customer = self.kwargs['customer']
    # #     queryset = LineItem.objects.filter(customer=Invoice.objects.get(customer=self.kwargs['customer']))
    # #     return queryset


    # def get(self,request,*args, **kwargs):
    #     self.object = self.get_object(queryset=LineItem.objects.filter(customer=Invoice.objects.get(customer=self.kwargs['customer'])))
    #     return super().get(request, *args, **kwargs)

  

    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object(queryset=LineItem.objects.filter(customer=Invoice.objects.get(customer=self.kwargs['customer'])))
    #     return super().post(request, *args, **kwargs)

    # def get_form(self, form_class=None):
    #     return AuthorBooksFormset(**self.get_form_kwargs(), instance=self.object)

    # def form_valid(self, form):
    #     form.save()
    #     print('saved')


    #     return HttpResponseRedirect(self.get_success_url())


    
    # def get_success_url(self):
    #     return reverse('books:author_detail', kwargs={'customer': self.object.customer})
        


        

    
