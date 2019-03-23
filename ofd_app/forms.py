from django import forms
from .models import Product
from .models import User
#from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from ofd_app import views

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name', 'product_cost')

class UserForm(forms.ModelForm):
    email = forms.EmailField(required = True)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'inn', 'phone_number', 'org', 'city')
    def __init__(self, *args, **kwargs):
        self.requested_user = kwargs.pop('requested_user', None)
        instance = kwargs.get('instance', None)
        if instance.is_user():
            kwargs.update(initial={'inn': instance.parent.inn, 'org': instance.parent.org})
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        if self.requested_user is not None and not self.requested_user.is_superuser:
            self.fields['inn'].widget.attrs['readonly'] = True
            self.fields['org'].widget.attrs['readonly'] = True
    def clean_inn(self):
        if self.requested_user is not None and not self.requested_user.is_superuser:
            return self.instance.inn
        return self.cleaned_data['inn']
    def clean_org(self):
        if self.requested_user is not None and not self.requested_user.is_superuser:
            return self.instance.org
        return self.cleaned_data['org']
    def clean_username(self):
        return self.instance.username

class UserCreationFormCustom(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'inn', 'phone_number', 'org', 'city')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
