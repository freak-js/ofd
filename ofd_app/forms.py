from django import forms
from .models import Product
from .models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name', 'product_cost')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('inn', 'org', 'city', 'is_legal')

class UserCreationFormCustom(UserCreationForm):
    city = forms.CharField(label="Город пользователя", max_length=100)
    inn = forms.CharField(label="ИНН", max_length = 12)
    org = forms.CharField(label="Организация", max_length=100)
    is_legal = forms.BooleanField(label="Юридичиское лицо?")
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'inn', 'org', 'city', 'password1', 'password2','is_legal')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
    def save(self):
        user = super().save(commit=True)
        profile = Profile(user=user, city=self.cleaned_data['city'], inn=self.cleaned_data['city'], org=self.cleaned_data['org'], is_legal=self.cleaned_data['is_legal'])
        profile.save()
        return user, profile
