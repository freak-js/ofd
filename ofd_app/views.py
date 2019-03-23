from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import QueryDict
from ofd_app.forms import ProductForm, UserForm, UserCreationFormCustom
from ofd_app.models import User, Product, ProductUserRel, Order, OrderProduct, OrderStatus
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required
from django import forms
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import FilteredRelation, Q, F
from django.contrib.auth import login

@login_required(login_url='/login/')
def product(request, **kwargs):
    if 'id' in kwargs:
        if not request.user.has_perm('ofd_app.change_product'):
            return redirect('products')
        product = get_object_or_404(Product, product_id=kwargs['id'])
        if request.method == 'POST':
            form = ProductForm(request.POST, instance = product)
            if form.is_valid():
                form.save()
        else:
            form = ProductForm(instance=product)
    elif request.method == 'POST':
        if not request.user.has_perm('ofd_app.add_product'):
            return redirect('products')
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
    else:
        if not request.user.has_perm('ofd_app.add_product'):
            return redirect('products')
        form = ProductForm()
    return render(request, 'ofd_app/index_product_add.html', {'form': form})

@login_required(login_url='/login/')
@permission_required('ofd_app.view_product', login_url='/products/')
def products(request):
    products = get_products(None if request.user.is_superuser else request.user);
    if request.method == 'POST':
        request.session['basket'] = []
        for product in products:
            input_id = 'product_to_basket_id_' + str(product.product_id)
            value = request.POST.get(input_id, '').strip()
            quantity = int(value) if value else 0
            if quantity > 0:
                request.session['basket'].append({'id': product.product_id, 'name': product.product_name, 'cost': product.by_user__cost if product.by_user__cost is not None else product.product_cost, 'quantity': quantity})
        return redirect('basket')
    return render(request, 'ofd_app/index_top.html', {'products': products, 'can_delete': request.user.has_perm('ofd_app.delete_product')})

@login_required(login_url='/login/')
def get_basket(request):
    products = []
    total = 0
    if request.method == 'POST':
        if 'basket' in request.session and len(request.session['basket']) > 0:
            basket_comment = request.POST.get('basket_comment', '').strip()
            order = Order(user = request.user, comment = basket_comment)
            order.save()
            for item in request.session['basket']:
                product = Product.objects.get(product_id=item['id'])
                ##TODO обработать ситуацию, когда продукта нет
                order_product = OrderProduct(order = order, product = product, amount = item['quantity'], cost = item['cost'])
                order_product.save()
            request.session.pop('basket')
    else:
        if 'basket' in request.session and len(request.session['basket']) > 0:
            for item in request.session['basket']:
                product = item
                product['sum'] = item['cost'] * item['quantity']
                products.append(product)
                total += product['sum']
    return render(request, 'ofd_app/basket.html', {'products': products, 'total': total})


@login_required(login_url='/login/')
#@csrf_exempt
@require_POST
@permission_required('ofd_app.delete_product', login_url='/products/')
def product_delete(request):
    ids = request.POST.getlist('product_to_delete')
    cnt_delete = 0
    for id in ids:
        try:
            product = Product.objects.get(product_id=id)
            product.product_is_active = False
            product.save()
            cnt_delete += 1
        except Product.DoesNotExist:
            pass
    return redirect('products')

@login_required(login_url='/login/')
#@csrf_exempt
def user(request, **kwargs):
    user = None
    if 'id' in kwargs:
        if not request.user.has_perm('ofd_app.change_user') and kwargs['id'] != request.user.id:
            return redirect('products')
        user = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            user_form = UserForm(request.POST, instance = user, requested_user = request.user)
            user_save(user_form, request.user)
        else:
            user_form = UserForm(instance = user, requested_user = request.user)
    elif request.method == 'POST':
        if not request.user.has_perm('ofd_app.change_user'):
            return redirect('products')
        user_form = UserCreationFormCustom(request.POST)
        user_save(user_form, request.user)
        return redirect('users')
    else:
        if not request.user.has_perm('ofd_app.view_user'):
            return redirect('products')
        user_form = UserCreationFormCustom()
    return render(request, 'ofd_app/user.html', {'user_form': user_form})

@login_required(login_url='/login/')
@permission_required('ofd_app.change_productuserrel', login_url='/products/')
def user_product(request, **kwargs):
    if 'id' in kwargs:
        user = get_object_or_404(User, id=kwargs['id'])
        if not user.groups.filter(name='Manager').exists():
            return redirect('users');
        if request.method == 'POST':
            save_product_user_rel(request.POST, user, request.user.id)
        products = get_products(user)
    return render(request, 'ofd_app/user_product.html', {'products': products})

@login_required(login_url='/login/')
@permission_required('ofd_app.view_user', login_url='/products/')
def users(request):
    if request.user.groups.filter(name='Manager').exists():
        users = User.objects.all().filter(is_active = True).filter(parent=request.user)
    else:
        users = User.objects.all().filter(is_active = True)
    return render(request, 'ofd_app/users.html', {'users': users, 'can_delete': request.user.has_perm('auth.delete_user')})

@login_required(login_url='/login/')
@require_POST
@permission_required('auth.delete_user', login_url='/products/')
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

@login_required(login_url='/login/')
def orders(request):
    if request.method == 'POST' and request.user.has_perm('ofd_app.manage_order_status'):
        ids = request.POST.getlist('order_ids')
        status = request.POST.get('status', '').strip()
        Order.assign_status(ids, status)
    orders = Order.objects.all().filter(user=request.user)
    order_data = []
    cnt = 0
    for order in orders:
        rels = OrderProduct.objects.all().filter(order=order)
        total = sum(i.amount * i.cost for i in rels)
        cnt += 1
        products = []
        for rel in rels:
            products.append({'product_name': rel.product.product_name, 'amount': rel.amount, 'cost': rel.cost, 'full_cost': rel.amount * rel.cost})
        order_data.append({'id': order.id, 'order_num': cnt, 'adddate': order.adddate, 'cnt_products': len(rels), 'total': total, 'comment': order.comment, 'products': products})
    return render(request, 'ofd_app/orders.html', {'orders': order_data})

#@login_required(login_url='/login/')
#def order(request, **kwargs):
#    if 'id' in kwargs:
#        order = get_object_or_404(Order, id=kwargs['id'])
#        if order.user.id != request.user.id:
#            return redirect('products')
#        rels = OrderProduct.objects.all().filter(order=order)
#        order_data = []
#        total = 0
#        for rel in rels:
#            total += rel.amount * rel.cost
#            order_data.append({'product_name': rel.product.product_name, 'amount': rel.amount, 'cost': rel.cost, 'full_cost': rel.amount * rel.cost})
#        return render(request, 'ofd_app/order.html', {'order': order_data, 'total': total})

def user_reg(request):
    if request.method == 'POST':
        reg_form = UserCreationFormCustom(request.POST)
        user = user_save(reg_form)
        if user is not None:
            login(request, user)
            return redirect('products')
    else:
        reg_form = UserCreationFormCustom()
    return render(request, 'ofd_app/user_reg.html', {'reg_form': reg_form})

def save_product_user_rel(costs, user, user_mod_id):
    products = Product.objects.all()
    for product in products:
        cost = costs.get('product_' + str(product.product_id))
        if cost is not None and int(cost.strip()) > 0 if cost else 0 > 0 :
            try:
                relation = ProductUserRel.objects.get(user=user, product=product)
                relation.cost = cost
                relation.user_mod = user_mod_id
            except ProductUserRel.DoesNotExist:
                relation = ProductUserRel(user=user, product=product, cost=cost, user_mod=user_mod_id)
            relation.save()

def get_products(user):
    if user is not None:
        if user.groups.filter(name='User').exists():
            filtered_user = user.parent
        else:
            filtered_user = user
        products = Product.objects.annotate(by_user=FilteredRelation('productuserrel', condition = Q(productuserrel__user=filtered_user))).filter(Q(by_user__isnull = True) | Q(by_user__user=filtered_user)).filter(product_is_active=True).values_list('product_id', 'product_name', 'product_cost', 'by_user__cost', named=True).order_by('product_cost')
    else:
        products = Product.objects.annotate(by_user=FilteredRelation('productuserrel', condition = Q(productuserrel__user=user))).filter(Q(by_user__isnull = True)).filter(product_is_active=True).values_list('product_id', 'product_name', 'product_cost', 'by_user__cost', named=True).order_by('product_cost')
    return products

def user_assign_group(user, group_name):
    group = Group.objects.get(name=group_name).user_set.add(user)

def user_resolve_group(user, request_user):
    group_name = 'Manager'
    if request_user is not None and request_user.groups.filter(name='Manager').exists():
        group_name = 'User'
    elif request_user is not None and request_user.is_superuser:
        group_name = 'Admin'
    user_assign_group(user, group_name)

def user_save(user_form, request_user=None):
    user = None
    if user_form.is_valid():
        user = user_form.save()
        ##Resolve group
        if user.groups.all().count() == 0 and not user.is_superuser:
            user_resolve_group(user, request_user)
        if user.parent is None and request_user is not None and request_user.groups.filter(name='Manager').exists():
            user.parent = request_user
            user.save()
    return user
