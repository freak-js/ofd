from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import QueryDict
from ofd_app.forms import ProductForm
from ofd_app.models import Product
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import get_object_or_404

@login_required(login_url='/login/')
def product(request, **kwargs):
    if 'id' in kwargs:
        product = get_object_or_404(Product, product_id=kwargs['id'])
        if request.method == 'POST':
            form = ProductForm(request.POST, instance = product)
            if form.is_valid():
                form.save()
        else:
            form = ProductForm(instance=product)
    elif request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
    else:
        form = ProductForm()
    return render(request, 'ofd_app/index_product_add.html', {'form': form})

@login_required(login_url='/login/')
def products(request):
    products = Product.objects.all().order_by('product_cost')
    return render(request, 'ofd_app/index_top.html', {'products': products})
