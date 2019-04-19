from django import forms
from .models import Product
from .models import User
#from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from ofd_app import views
from django.utils.translation import gettext_lazy as _

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name', 'product_cost')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'inn', 'phone_number', 'org', 'city')
        labels = {'username': _('Логин'), 'city': _('Город')}

    def __init__(self, *args, **kwargs):
        self.requested_user = kwargs.pop('requested_user', None)
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        if self.can_change_inn_org():
            self.fields['inn'].widget.attrs['readonly'] = True
            self.fields['org'].widget.attrs['readonly'] = True
    def clean_inn(self):
        if self.can_change_inn_org():
            return self.instance.inn
        return self.cleaned_data['inn']
    def clean_org(self):
        if self.can_change_inn_org():
            return self.instance.org
        return self.cleaned_data['org']
    def clean_username(self):
        return self.instance.username
    def can_change_inn_org(self):
        return self.requested_user is not None and not (self.requested_user.is_superuser or self.requested_user.is_admin()) or self.instance.is_user()

class UserCreationFormCustom(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'inn', 'phone_number', 'org', 'city')
        labels = {'username': _('Логин'), 'city': _('Город')}

    def __init__(self, *args, **kwargs):
        self.requested_user = kwargs.pop('requested_user', None)
        super().__init__(*args, **kwargs)
        if self.requested_user is not None and self.requested_user.is_manager():
            self.fields.pop('inn')
            self.fields.pop('org')
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
