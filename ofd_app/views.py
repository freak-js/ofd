from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import QueryDict
from ofd_app.forms import ProductForm
from ofd_app.models import Product
from django.contrib.auth.decorators import login_required
from django import forms

@login_required(login_url='/login/')
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
    else:
        form = ProductForm()
    return render(request, 'ofd_app/index_product_add.html', {'form': form})

@login_required(login_url='/login/')
def product_get_all(request):
    products = Product.objects.all()
    return render(request, 'ofd_app/index_top.html', {'products': products})
