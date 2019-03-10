from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import QueryDict
from ofd_app.forms import ProductForm
from ofd_app.forms import UserForm
from ofd_app.forms import ProfileForm
from ofd_app.forms import UserCreationFormCustom
from ofd_app.models import Product
from ofd_app.models import ProductUserRel
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import FilteredRelation, Q, F

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
    return render(request, 'ofd_app/index_top.html', {'products': get_products(None)})

@login_required(login_url='/login/')
#@csrf_exempt
@require_POST
def product_delete(request):
    ids = request.POST.getlist('product_to_delete')
    cnt_delete = 0
    for id in ids:
        try:
            Product.objects.get(product_id=id).delete()
            cnt_delete += 1
        except Product.DoesNotExist:
            pass
    return redirect('products')

@login_required(login_url='/login/')
#@csrf_exempt
def user(request, **kwargs):
    user = None
    if 'id' in kwargs:
        user = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            user_form = UserForm(request.POST, instance = user)
            try:
                profile_form = ProfileForm(request.POST, instance = user.profile)
            except User.profile.RelatedObjectDoesNotExist:
                profile_form = ProfileForm(request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile = profile_form.save(commit = False)
                profile.user = user
                profile.save()
        else:
            user_form = UserForm(instance = user)
            try:
                profile_form = ProfileForm(instance = user.profile)
            except User.profile.RelatedObjectDoesNotExist:
                profile_form = ProfileForm()
    elif request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        ##TODO: implement via @receiver
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit = False)
            profile.user = user
            profile.save()
    else:
        user_form = UserForm()
        profile_form = ProfileForm()
    return render(request, 'ofd_app/user.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required(login_url='/login/')
def user_product(request, **kwargs):
    #TODO проверить права на сохранение цен для продуктов
    if 'id' in kwargs:
        user = get_object_or_404(User, id=kwargs['id'])
        try:
            profile = user.profile
        except User.profile.RelatedObjectDoesNotExist:
            return redirect('users')
        if request.method == 'POST':
            save_product_user_rel(request.POST, profile, request.user.id)
        products = get_products(profile)
    return render(request, 'ofd_app/user_product.html', {'products': products})

@login_required(login_url='/login/')
def users(request):
    users = User.objects.all().filter(is_active = True)
    return render(request, 'ofd_app/users.html', {'users': users})

@login_required(login_url='/login/')
@require_POST
def user_delete(request):
    ids = request.POST.getlist('user_to_delete')
    cnt_delete = 0
    for id in ids:
        try:
            user = User.objects.get(id=id)
            user.is_active = False
            user.save()
            cnt_delete += 1
        except User.DoesNotExist:
            pass
    return redirect('users')

def user_reg(request):
    if request.method == 'POST':
        reg_form = UserCreationFormCustom(request.POST)
        if reg_form.is_valid():
            reg_form.save()
            return redirect('login')
    else:
        reg_form = UserCreationFormCustom()
    return render(request, 'ofd_app/user_reg.html', {'reg_form': reg_form})

def save_product_user_rel(costs, profile, user_mod_id):
    products = Product.objects.all()
    for product in products:
        cost = costs.get('product_' + str(product.product_id))
        if cost is not None and int(cost.strip()) > 0 if cost else 0 > 0 :
            try:
                relation = ProductUserRel.objects.get(user=profile, product=product)
                relation.cost = cost
                relation.user_mod = user_mod_id
            except ProductUserRel.DoesNotExist:
                relation = ProductUserRel(user=profile, product=product, cost=cost, user_mod=user_mod_id)
            relation.save()

def get_products(profile):
    if profile is not None and profile.products.count() > 0:
        products = Product.objects.annotate(by_user=FilteredRelation('productuserrel', condition = Q(productuserrel__user=profile))).filter(Q(by_user__isnull = True) | Q(by_user__user=profile)).values_list('product_id', 'product_name', 'product_cost', 'by_user__cost', named=True).order_by('product_cost')
        print(products.query)
    else:
        products = Product.objects.all().values('product_id', 'product_name', 'product_cost').order_by('product_cost')
    return products
