from django import forms
from .models import Product
from .models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from ofd_app import views

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name', 'product_cost')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class ProfileForm(forms.ModelForm):
    parent = forms.ModelChoiceField(label="Менеджер", queryset=User.objects.filter(groups__name__in=['Manager']))
    class Meta:
        model = Profile
        fields = ('inn', 'phone_number', 'org', 'city', 'parent', 'is_legal')
    def __init__(self, *args, hideParent, **kwargs):
        super().__init__(*args, **kwargs)
        if hideParent:
            self.fields.pop('parent')

class UserCreationFormCustom(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
