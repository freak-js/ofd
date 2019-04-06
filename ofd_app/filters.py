from ofd_app.utils import to_int
from datetime import datetime
from datetime import date
from datetime import timedelta

def date_filter_format():
    return "%Y-%m-%d";

def apply_user_filters(request, key):
    if key not in request.session:
        save_user_filters(request.session, key)
    if request.method == 'POST' and request.POST.get('date_filter_button', '') == 'add_filter':
        org = request.POST.get('org_filter', '').strip()
        save_user_filters(request.session, key, org)

def apply_order_filters(request, key):
    if key not in request.session:
        save_order_filters(request.session, key)
    if request.method == 'POST' and request.POST.get('date_filter_button', '') == 'add_filter':
        date_from = request.POST.get('date_from', '').strip()
        date_to = request.POST.get('date_to', '').strip()
        org = request.POST.get('org_filter', '').strip()
        status = request.POST.get('status_filter', '').strip()
        user = request.POST.get('user_filter', '').strip()
        try:
            datetime.strptime(date_from, date_filter_format())
            datetime.strptime(date_to, date_filter_format())
            save_order_filters(request.session, key, date_from, date_to, status, org, user)
        except ValueError:
            save_order_filters(request.session, key)

def save_order_filters(session, key, date_from = None, date_to = None, status = None, org = None, user= None):
    if key not in session:
        session[key] = {}
    if date_from is None or date_to is None:
        session[key]['date_from'] = date.today().strftime(date_filter_format())
        session[key]['date_to'] = (date.today() + timedelta(1)).strftime(date_filter_format())
    else:
        session[key]['date_from'] = date_from
        session[key]['date_to'] = date_to
    session[key]['org'] = org if org is not None and len(org) > 0 else '*'
    session[key]['status'] = status if status is not None and len(status) > 0 else '*'
    session[key]['user'] = user if user is not None and to_int(user, 0) > 0 else '*'
    session.save()

def save_user_filters(session, key, org = None):
    if key not in session:
        session[key] = {}
    session[key]['org'] = org if org is not None and len(org) > 0 else '*'
    session.save()