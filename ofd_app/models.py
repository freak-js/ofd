from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key = True)
    product_name = models.CharField("Имя продукта", max_length = 100, unique=True)
    product_moddate = models.DateTimeField("Дата модификации продукта", auto_now = True)
    product_adddate = models.DateTimeField("Дата добавления продукта", auto_now_add = True)
    product_cost = models.IntegerField("Базовая стоимость продукта", )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, primary_key = True)
    city = models.CharField("Город пользователя", max_length=100, null=True)
    inn = models.CharField("ИНН", max_length = 12, unique=True)
    org = models.CharField("Организация", max_length=100, null=True)
    is_legal = models.BooleanField("Юридичиское лицо?", default=False)
    parent = models.ForeignKey(User, models.SET_NULL, null=True, related_name='children')
    products = models.ManyToManyField(Product, through="ProductUserRel", verbose_name="Продукты доступные пользователю")
    phone_number = models.CharField("Номер телефона", max_length = 18, unique=True)

#@receiver(post_save, sender=User)
#def create_or_update_user_profile(sender, instance, created, **kwargs):
#    if created:
#        Profile.objects.create(user=instance)
#    instance.profile.save()


class ProductUserRel(models.Model):
  user = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="Пользователь")
  product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
  cost = models.IntegerField("Стоимость продукта",)
  moddate = models.DateTimeField("Дата модификации связи", auto_now=True)
  adddate = models.DateTimeField("Дата добавления связи", auto_now_add=True)
  user_mod = models.IntegerField("Пользователь, который последний раз модифицировал запись",)
  class Meta:
    unique_together = ('user', 'product')
