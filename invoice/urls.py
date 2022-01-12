from django.contrib import admin
from django.urls import path
from .views import InvoiceListView, createInvoice, generate_PDF, view_PDF
from .views import *
from django.contrib.auth import views as auth_views
app_name = 'invoice'

urlpatterns = [
    path('', InvoiceListView.as_view(), name="invoice-list"),
    path('create/', createInvoice, name="invoice-create"),
    path('invoice-detail/<id>', view_PDF, name='invoice-detail'),
    path('invoice-download/<id>', generate_PDF, name='invoice-download'),
    path('update/<int:pk>',
         invoiceupdate.as_view(),name='invoiceupdate'),
    path('productupdate/<int:pk>',
         productupdate.as_view(),name='productupdate'),


    path('test/<customer>',product_view,name='test'),
    path('edit/<customer>',edit_product, name="edit_product"),
#     path('authors/books/edit/<customer>', AuthorProductEditView.as_view(), name='author_book_edit'),
    path('update_order/<customer>/', createOrder, name="update_order"),
]
