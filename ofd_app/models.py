from django.db import models
#from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key = True)
    product_name = models.CharField("Имя продукта", max_length = 100, unique=True)
    product_moddate = models.DateTimeField("Дата модификации продукта", auto_now = True)
    product_adddate = models.DateTimeField("Дата добавления продукта", auto_now_add = True)
    product_cost = models.IntegerField("Базовая стоимость продукта", )
    product_is_active = models.BooleanField("Продукт активен?", default=True)

class User(AbstractUser):
    city = models.CharField("Город пользователя", max_length=100, null=True, blank=True)
    inn = models.CharField("ИНН", max_length = 12, null=True, blank=True)
    org = models.CharField("Организация", max_length=100, null=True)
    is_legal = models.BooleanField("Юридичиское лицо?", default=False)
    parent = models.ForeignKey("self", models.SET_NULL, null=True, related_name='children')
    products = models.ManyToManyField(Product, through="ProductUserRel", verbose_name="Продукты доступные пользователю")
    phone_number = models.CharField("Номер телефона", max_length = 18)

    def is_manager(self, user=None):
        user = self if user is None else user
        return user.groups.filter(name='Manager').exists()
    def is_user(self, user=None):
        user = self if user is None else user
        return user.groups.filter(name='User').exists()
    def is_admin(self, user=None):
        user = self if user is None else user
        return user.groups.filter(name='Admin').exists()

class ProductUserRel(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
  product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
  cost = models.IntegerField("Стоимость продукта",)
  moddate = models.DateTimeField("Дата модификации связи", auto_now=True)
  adddate = models.DateTimeField("Дата добавления связи", auto_now_add=True)
  user_mod = models.IntegerField("Пользователь, который последний раз модифицировал запись",)
  class Meta:
    unique_together = ('user', 'product')

class Order(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Номер заказа")
  products = models.ManyToManyField(Product, through="OrderProduct", verbose_name="Продукты заказанные пользователем")
  adddate = models.DateTimeField("Дата добавления заказа", auto_now_add=True)
  comment = models.TextField("Комментарий к заказу", null=True)

class OrderProduct(models.Model):
  order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name="Отношение к номеру заказа")
  product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Отношение к продукту")
  amount = models.IntegerField("Количество")
  cost = models.IntegerField("Итоговая стоимость для одного продукта")
