from ofd_app.utils import to_int
from datetime import datetime
from datetime import date
from datetime import timedelta

def date_filter_format():
    return "%Y-%m-%d"

def save_filters(request, key, apply_filters):
    session = request.session
    if 'date_from' in apply_filters and 'date_to' in apply_filters:
        if apply_filters['date_from'] is None or apply_filters['date_to'] is None:
            if (request.user.is_manager() or request.user.is_user()):
                session[key]['date_from'] = (date.today() - timedelta(90)).strftime(date_filter_format())
                session[key]['date_to'] = (date.today() + timedelta(1)).strftime(date_filter_format())
            else:
                session[key]['date_from'] = (date.today() - timedelta(6)).strftime(date_filter_format())
                session[key]['date_to'] = (date.today() + timedelta(1)).strftime(date_filter_format())
        else:
            session[key]['date_from'] = apply_filters['date_from']
            session[key]['date_to'] = apply_filters['date_to']
    if 'org' in apply_filters:
        session[key]['org'] = apply_filters['org'] if apply_filters['org'] is not None and len(apply_filters['org']) > 0 else '*'
    if 'status' in apply_filters:
        session[key]['status'] = apply_filters['status'] if apply_filters['status'] is not None and len(apply_filters['status']) > 0 else '*'
    if 'user' in apply_filters:
        user_id = to_int(apply_filters['user'], 0) 
        session[key]['user'] = user_id if apply_filters['user'] is not None and user_id > 0 else '*'
    session.save()

def save_default_values(request, key, filters):
    session = request.session
    session[key] = {}
    if 'date' in filters:
        if (request.user.is_manager() or request.user.is_user()):
            session[key]['date_from'] = (date.today() - timedelta(90)).strftime(date_filter_format())
            session[key]['date_to'] = (date.today() + timedelta(1)).strftime(date_filter_format())
        else:
            session[key]['date_from'] = (date.today() - timedelta(6)).strftime(date_filter_format())
            session[key]['date_to'] = (date.today() + timedelta(1)).strftime(date_filter_format())
    if 'org' in filters:
        session[key]['org'] = '*'
    if 'status' in filters:
        session[key]['status'] = '*'
    if 'user' in filters:
        session[key]['user'] = '*'
    session.save()

def apply_filters(request, key, filters = {'date'}):
    if key not in request.session:
        save_default_values(request, key, filters)
    if request.method == 'POST' and request.POST.get('date_filter_button', '') == 'add_filter':
        apply_filters = {}
        if 'date' in filters:
            date_from = request.POST.get('date_from', '').strip()
            date_to = request.POST.get('date_to', '').strip()
            try:
                datetime.strptime(date_from, date_filter_format())
                datetime.strptime(date_to, date_filter_format())
                apply_filters['date_from'] = date_from
                apply_filters['date_to'] = date_to
            except ValueError:
                apply_filters['date_from'] = None
                apply_filters['date_to'] = None
        if 'org' in filters:
            apply_filters['org'] = request.POST.get('org_filter', '').strip()
        if 'status' in filters:
            apply_filters['status'] = request.POST.get('status_filter', '').strip()
        if 'user' in filters:
            apply_filters['user'] = request.POST.get('user_filter', '').strip()
        save_filters(request, key, apply_filters)
