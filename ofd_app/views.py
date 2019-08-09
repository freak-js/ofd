from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import QueryDict
from ofd_app.forms import ProductForm, UserForm, UserCreationFormCustom
from ofd_app.models import User, Product, ProductUserRel, Order, OrderStatus
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required
from django import forms
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from datetime import datetime
from datetime import date
from datetime import timedelta
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from ofd_app.filters import date_filter_format
from ofd_app.filters import apply_filters
from ofd_app.utils import to_int, get_pages_list
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from ofd_app.constants import PRODUCTS, USERS, ORDERS, MY_CARD, STAT, FEEDBACK, INSTRUCTION, TEMPLATE_EMAIL_NEW_LOGIN_ADMIN_SUBJECT, TEMPLATE_EMAIL_NEW_LOGIN_ADMIN_BODY, TEMPLATE_EMAIL_NEW_LOGIN_USER_SUBJECT, TEMPLATE_EMAIL_NEW_LOGIN_USER_BODY, TEMPLATE_EMAIL_NEW_ORDER_USER_SUBJECT, TEMPLATE_EMAIL_NEW_ORDER_USER_BODY, TEMPLATE_EMAIL_NEW_ORDER_ADMIN_SUBJECT, TEMPLATE_EMAIL_NEW_ORDER_ADMIN_BODY , TEMPLATE_EMAIL_ORDER_STATUS_USER_SUBJECT, TEMPLATE_EMAIL_ORDER_STATUS_USER_BODY, MESSAGES
from django.core.mail import send_mail
from ofd.settings import EMAIL_HOST_USER, TIME_ZONE
from django.utils.timezone import pytz

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
    else:
        if not request.user.has_perm('ofd_app.add_product'):
            return redirect('products')
        if request.method == 'POST':
            form = ProductForm(request.POST)
            if form.is_valid():
                product = form.save()
        else:
            form = ProductForm()
    return render(request, 'ofd_app/index_product_add.html', {'form': form, 'user_role': request.user.get_role(), 'path': PRODUCTS})

@login_required(login_url='/login/')
@permission_required('ofd_app.view_product', login_url='/products/')
def products(request):
    if request.method == 'POST':
        product_id = to_int(request.POST.get('product_id', '').strip(), 0)
        order_comment = request.POST.get('order_comment', '').strip()
        quantity = to_int(request.POST.get('quantity', '').strip(), 1)
        if product_id > 0:
            product = request.user.get_product(product_id)
            if product is not None:
                cost = product.by_user__cost if product.by_user__cost is not None and product.by_user__cost > 0 else product.product_cost
                db_product = Product.objects.get(product_id=product_id)
                order = Order(user = request.user, product=db_product, comment = order_comment, amount = quantity, cost = cost, is_paid = False)
                order.save()
                send_mail(TEMPLATE_EMAIL_NEW_ORDER_ADMIN_SUBJECT, TEMPLATE_EMAIL_NEW_ORDER_ADMIN_BODY.format(first_name = request.user.first_name , last_name = request.user.last_name, corg=request.user.org, product = db_product.product_name , amount = quantity , total = quantity * cost ), EMAIL_HOST_USER, [EMAIL_HOST_USER], fail_silently=False,)
                send_mail(TEMPLATE_EMAIL_NEW_ORDER_USER_SUBJECT, TEMPLATE_EMAIL_NEW_ORDER_USER_BODY.format(number = order.id, date = order.adddate.astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y.%m.%d %H:%M:%S"), product = db_product.product_name, amount = quantity , total = quantity * cost ), EMAIL_HOST_USER, [request.user.email], fail_silently=False,)
                return redirect('orders')
        ##TODO передать сообщение об ошибке
        return redirect('products')
    return render(request, 'ofd_app/index_top.html', {'products': request.user.get_products(), 'can_delete': request.user.has_perm('ofd_app.delete_product'), 'user_role': request.user.get_role(), 'path': PRODUCTS})

@require_POST
@login_required(login_url='/login/')
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
def user(request, **kwargs):
    user = None
    my_card = False
    if 'id' in kwargs:
        my_card = request.user.id == kwargs['id']
        if not request.user.has_perm('ofd_app.change_user') and not my_card:
            return redirect('products')
        user = get_object_or_404(User, id=kwargs['id'])
        if not request.user.has_access_to_user(user):
            return redirect('products')
        if request.method == 'POST':
            user_form = UserForm(request.POST, instance = user, requested_user = request.user)
            user_save(user_form, request.user)
        else:
            user_form = UserForm(instance = user, requested_user = request.user)
    elif request.method == 'POST':
        if not request.user.has_perm('ofd_app.change_user'):
            return redirect('products')
        user_form = UserCreationFormCustom(request.POST, requested_user = request.user)
        user = user_save(user_form, request.user)
        if user is not None:
            return redirect('users')
    else:
        if not request.user.has_perm('ofd_app.view_user'):
            return redirect('products')
        user_form = UserCreationFormCustom(requested_user = request.user)
    return render(request, 'ofd_app/user.html', {'user_form': user_form, 'user_role': request.user.get_role(), 'path': MY_CARD if my_card else USERS})

@login_required(login_url='/login/')
@permission_required('ofd_app.change_productuserrel', login_url='/products/')
def user_product(request, **kwargs):
    if 'id' in kwargs:
        user = get_object_or_404(User, id=kwargs['id'])
        if not user.is_manager():
            return redirect('users')
        if request.method == 'POST':
            ProductUserRel.save_product_user_rel(request.POST, user, request.user.id)
        products = user.get_products()
    return render(request, 'ofd_app/user_product.html', {'products': products, 'path': USERS})

@login_required(login_url='/login/')
@permission_required('ofd_app.view_user', login_url='/products/')
def users(request):
    apply_filters(request, 'user_filters', {'org'})
    filters = {}
    if request.user.groups.filter(name='Manager').exists():
        users = User.objects.all().filter(is_active = True).filter(is_superuser=False).filter(parent=request.user)
    else:
        org = request.session['user_filters']['org']
        users = User.objects.all().filter(is_active = True).filter(is_superuser=False).filter(groups__name__in=['Manager', 'Admin'])
        if request.user.is_admin():
            users = users.filter(groups__name__in=['Manager'])
        if org is not None and len(org) > 0 and org != '*':
            users = users.filter(org=org)
        filters['org'] = User.get_organizations()
    user_data = []
    for user in users:
        data = user.__dict__
        data['role'] = user.get_role()
        data['childs'] = user.get_childs()
        user_data.append(data)
    return render(request, 'ofd_app/users.html', {'users': construct_pagination(request, user_data), 'can_delete': request.user.has_perm('ofd_app.delete_user'), 'filters': filters, 'user_role': request.user.get_role(), 'path': USERS})

@require_POST
@login_required(login_url='/login/')
@permission_required('ofd_app.delete_user', login_url='/products/')
def user_delete(request):
    ids = request.POST.getlist('user_to_delete')
    cnt_delete = 0
    for id in ids:
        if to_int(id, 0) > 0:
            try:
                user = User.objects.get(id=id)
                if request.user.has_access_to_user(user):
                    user.is_active = False
                    user.save()
                    cnt_delete += 1
            except User.DoesNotExist:
                pass
    return redirect('users')

@login_required(login_url='/login/')
def orders(request):
    date = datetime.now()
    apply_filters(request, 'order_filters', {'date', 'status', 'org', 'user', 'paid'})
    if request.method == 'POST' and request.user.has_perm('ofd_app.manage_order_status'):
        id = to_int(request.POST.get('order_id', 0), 0)
        status = request.POST.get('status', '').strip()
        admin_comment = request.POST.get('admin_comment', '').strip()
        codes = request.POST.get('order_codes', '').strip()
        if id > 0 and len(status) > 0:
            try:
                order = Order.objects.get(id=id)
                op_result = order.assign_status(status, admin_comment, codes)
                if op_result:
                    send_mail(TEMPLATE_EMAIL_ORDER_STATUS_USER_SUBJECT, TEMPLATE_EMAIL_ORDER_STATUS_USER_BODY.format(number = id, date = order.adddate.astimezone(pytz.timezone(TIME_ZONE)).strftime("%Y.%m.%d %H:%M:%S"), total = order.amount * order.cost, product = order.product.product_name, amount = order.amount, status = MESSAGES[1] if status == 'R' else MESSAGES[2], comment = admin_comment), EMAIL_HOST_USER, [order.user.email], fail_silently=False,)
            except Order.DoesNotExist:
                pass
    date_from = datetime.strptime(request.session['order_filters']['date_from'], date_filter_format())
    date_to = datetime.strptime(request.session['order_filters']['date_to'], date_filter_format())
    org = request.session['order_filters']['org']
    status = request.session['order_filters']['status']
    user = request.session['order_filters']['user']
    paid = request.session['order_filters']['paid']
    orders = Order.get_orders(request.user, date_from, date_to, status, org, user, paid)
    order_data = []
    for order in orders:
        product = {'product_name': order.product.product_name, 'amount': order.amount, 'cost': order.cost, 'full_cost': order.amount * order.cost}
        order_data.append({'id': order.id, 'adddate': order.adddate.astimezone(pytz.timezone(TIME_ZONE)).strftime("%d.%m.%y %H:%M"), 'comment': order.comment, 'product': product, 'status': order.status.code, 'user': order.user, 'user_role': order.user_role, 'admin_comment': order.admin_comment, 'codes': order.codes, 'is_paid' : order.is_paid})
    filters = {}
    if request.user.is_superuser or request.user.is_admin():
        filters['org'] = User.get_organizations()
    elif request.user.is_manager():
        filters['users'] = [{'id': request.user.id, 'first_name': request.user.first_name, 'last_name': request.user.last_name}]
        for item in request.user.get_childs():
            child = {'id': item['id'], 'first_name': item['first_name'], 'last_name': item['last_name']}
            filters['users'].append(child)
    filters['status'] = OrderStatus.get_all_statuses()
    return render(request, 'ofd_app/orders.html', {'orders': construct_pagination(request, order_data), 'filters': filters, 'user_role': request.user.get_role(), 'path': ORDERS})

@login_required(login_url='/login/')
def stat_org(request):
    apply_filters(request, 'stat_org', {'date'})
    date_from = datetime.strptime(request.session['stat_org']['date_from'], date_filter_format())
    date_to = datetime.strptime(request.session['stat_org']['date_to'], date_filter_format()) + timedelta(1)
    sql = '''
    select 1 as id
         , u.org
         , u.inn
         , coalesce(sum(case when q.status = 'A' then q.total else 0 end), 0) as total
         , count(q.order_id) as cnt_all
         , sum(case when q.status = 'A' then 1 else 0 end) as cnt_approve
         , sum(case when q.status = 'I' then 1 else 0 end) as cnt_in_progress
         , sum(case when q.status = 'R' then 1 else 0 end) as cnt_reject
        from ofd_app_user u
            left outer join (
                select ug.user_id
                 from ofd_app_user_groups ug
                      inner join auth_group ag
                              on ug.group_id = ag.id
                where ag.name = 'Admin'
            ) ad on u.id = ad.user_id
            left outer join
            (
            select o.user_id
                 , o.id as order_id
                 , o.status_id as status
                 , o.amount * o.cost as total
              from ofd_app_order o
             where adddate >= %s
               and adddate < %s
            ) q on u.id = q.user_id
     where u.is_superuser = false
       and ad.user_id is null
    group by org, inn
    union
    select 1 as id
         , 'Общий итог' as org
         , '' as inn
         , coalesce(sum(case when o.status_id = 'A' then o.amount * o.cost else 0 end), 0) as total
         , count(o.id) as cnt_all
         , sum(case when o.status_id = 'A' then 1 else 0 end) as cnt_approve
         , sum(case when o.status_id = 'I' then 1 else 0 end) as cnt_in_progress
         , sum(case when o.status_id = 'R' then 1 else 0 end) as cnt_reject
      from ofd_app_order o
           inner join ofd_app_user u on o.user_id = u.id
           left outer join (
                select ug.user_id
                 from ofd_app_user_groups ug
                      inner join auth_group ag
                              on ug.group_id = ag.id
                where ag.name = 'Admin'
            ) ad on u.id = ad.user_id
     where u.is_superuser = false
       and ad.user_id is null
       and adddate >= %s
       and adddate < %s
    order by total desc
    '''
    result = User.objects.raw(sql, [date_from, date_to, date_from, date_to])
    data = []
    for row in result:
        item = {'org': row.org, 'inn': row.inn, 'total': row.total, 'cnt_all': row.cnt_all, 'cnt_approve': row.cnt_approve, 'cnt_in_progress': row.cnt_in_progress, 'cnt_reject': row.cnt_reject}
        data.append(item) 
    for i in data:
        if i['org'] == 'Общий итог':
            grand_total = i
    return render(request, 'ofd_app/stat_org.html', {'stat': construct_pagination(request, data), 'user_role': request.user.get_role(), 'path': STAT, 'grand_total' : grand_total})

@login_required(login_url='/login/')
def exportxlsx(request, **kwargs):
    if 'id' in kwargs:
        wb = Workbook()
        ws = wb.active
        db_codes = Order.get_order_codes(request.user, kwargs['id'])
        codes = db_codes.split()
        ix = 1
        for code in codes:
            col = 'A' + str(ix)
            ws[col] = code
            ix = ix + 1
        response = HttpResponse(save_virtual_workbook(wb), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=codes.xlsx'
        return response

@login_required(login_url='/login/')
def exporttxt(request, **kwargs):
    if 'id' in kwargs:
        db_codes = Order.get_order_codes(request.user, kwargs['id'])
        codes = db_codes.split()
        response = HttpResponse('\r\n'.join(codes), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=codes.txt'
        return response

def construct_pagination(request, data):
    page        = to_int(request.GET.get('page', 1), 1)
    p           = Paginator(data, 10)
    page_object = p.get_page(page)
    pagination  = {
                'page' : page if 0 < page <= p.num_pages else p.num_pages,
                'data' : page_object.object_list,
                'prev' : page_object.previous_page_number() if page_object.has_previous() else None,
                'next' : page_object.next_page_number() if page_object.has_next() else None,
                'count': get_pages_list(int(p.num_pages), page if 0 < page <= p.num_pages else p.num_pages)
                }
    return pagination

def user_reg(request):
    if request.method == 'POST':
        reg_form = UserCreationFormCustom(request.POST)
        user = user_save(reg_form)
        if user is not None:
            send_mail(TEMPLATE_EMAIL_NEW_LOGIN_ADMIN_SUBJECT, TEMPLATE_EMAIL_NEW_LOGIN_ADMIN_BODY.format(first_name = user.first_name , last_name = user.last_name , email = user.email , phone_number = user.phone_number , org = user.org , city = user.city ), EMAIL_HOST_USER, [EMAIL_HOST_USER], fail_silently=False,)
            send_mail(TEMPLATE_EMAIL_NEW_LOGIN_USER_SUBJECT.format(first_name = user.first_name), TEMPLATE_EMAIL_NEW_LOGIN_USER_BODY.format(login = user.username), EMAIL_HOST_USER, [user.email], fail_silently=False,)
            login(request, user)
            return redirect('products')
    else:
        reg_form = UserCreationFormCustom()
    return render(request, 'ofd_app/user_reg.html', {'reg_form': reg_form})

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
        if user.parent is None and user.is_user() and request_user is not None and request_user.is_manager():
            user.parent = request_user
        if user.is_user() and (user.inn is None or user.org is None or len(user.inn) == 0 or len(user.org) == 0):
            user.inn = user.parent.inn
            user.org = user.parent.org
        user.save()
    return user

@login_required(login_url='/login/')
def feedback(request):
    return render(request, 'ofd_app/feedback.html', {'user_role': request.user.get_role(), 'path': FEEDBACK})

@login_required(login_url='/login/')
def instruction(request):
    return render(request, 'ofd_app/instruction.html', {'user_role': request.user.get_role(), 'path': INSTRUCTION})

def contacts(request):
    return render(request, 'ofd_app/contacts.html')

@require_POST
@login_required(login_url='/login/')
def order_change_pay_sign(request):
    if not (request.user.is_superuser or request.user.is_admin()):
        return redirect('orders')

    ids = request.POST.getlist('is_paid')

    for id in ids:
        if to_int(id, 0) > 0:
            try:
                order = Order.objects.get(id=id)
                order.is_paid = not order.is_paid
                order.save()
            except Order.DoesNotExist:
                pass
    return redirect('orders')

@require_POST
@login_required(login_url='/login/')
def change_order(request):
    if not (request.user.is_superuser or request.user.is_admin()):
        return redirect('orders')

    new_cost   = to_int(request.POST.get('cost', '').strip(), 0)
    new_amount = to_int(request.POST.get('amount', '').strip(), 0)
    order_id   = to_int(request.POST.get('order_id', '').strip(), 0)

    if order_id > 0 and new_amount > 0 and new_cost > 0:
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return redirect('orders')
        order.amount = new_amount
        order.cost   = new_cost
        order.save()
    return redirect('orders')

