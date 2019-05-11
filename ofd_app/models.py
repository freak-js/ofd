# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import FilteredRelation, Q, F

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key = True)
    product_name = models.CharField("Имя продукта", max_length = 100, unique=True)
    product_moddate = models.DateTimeField("Дата модификации продукта", auto_now = True)
    product_adddate = models.DateTimeField("Дата добавления продукта", auto_now_add = True)
    product_cost = models.IntegerField("Базовая стоимость продукта", )
    product_is_active = models.BooleanField("Продукт активен?", default=True)

class User(AbstractUser):
    email = models.EmailField("Email")
    city = models.CharField("Город проживания", max_length=100, null=True, blank=True)
    inn = models.CharField("ИНН", max_length = 12)
    org = models.CharField("Организация", max_length=100)
    is_legal = models.BooleanField("Юридичиское лицо?", default=False)
    parent = models.ForeignKey("self", models.SET_NULL, null=True, related_name='children')
    products = models.ManyToManyField(Product, through="ProductUserRel", verbose_name="Продукты доступные пользователю")
    phone_number = models.CharField("Номер телефона", max_length = 18)

    def save(self, *args, **kwargs):
        if self.id is not None and self.is_manager():
            need_update_childs = False
            db_object = User.objects.get(id=self.id)
            if db_object.inn != self.inn:
                need_update_childs = True
            if db_object.org != self.org:
                need_update_childs = True
            if db_object.is_active != self.is_active:
                need_update_childs = True
            if need_update_childs:
                childs = self.get_childs(False)
                for user in childs:
                    user.inn = self.inn
                    user.org = self.org
                    user.is_active = self.is_active
                    user.save()
        super().save(*args, **kwargs)

    def is_manager(self, user=None):
        user = self if user is None else user
        return user.groups.filter(name='Manager').exists()

    def is_user(self, user=None):
        user = self if user is None else user
        return user.groups.filter(name='User').exists()

    def is_admin(self, user=None):
        user = self if user is None else user
        return user.groups.filter(name='Admin').exists()

    def get_childs(self, as_dict=True):
        users = User.objects.filter(parent=self).order_by('username')
        return users.values() if as_dict else users

    def get_role(self):
        if self.is_admin():
            return 'Admin'
        elif self.is_manager():
            return 'Manager'
        elif self.is_user():
            return 'User'
        elif self.is_superuser:
            return 'God'

    def get_products(self):
        if self.is_user():
            filtered_user = self.parent
        else:
            filtered_user = self
        products = Product.objects.annotate(by_user=FilteredRelation('productuserrel', condition = Q(productuserrel__user=filtered_user))).filter(Q(by_user__isnull = True) | Q(by_user__user=filtered_user)).filter(product_is_active=True).values_list('product_id', 'product_name', 'product_cost', 'by_user__cost', named=True).order_by('product_cost')
        return products

    def get_product(self, product_id):
        if self.is_user():
            filtered_user = self.parent
        else:
            filtered_user = self
        products = Product.objects.annotate(by_user=FilteredRelation('productuserrel', condition = Q(productuserrel__user=filtered_user))).filter(Q(by_user__isnull = True) | Q(by_user__user=filtered_user)).filter(product_is_active=True).filter(product_id=product_id).values_list('product_id', 'product_name', 'product_cost', 'by_user__cost', named=True).order_by('product_name')
        return products[0] if len(products) > 0 else None

    @staticmethod
    def get_organizations():
        orgs = User.objects.exclude(org__isnull=True).exclude(org='').values('org').distinct().order_by('org')
        return list(map(lambda x: { 'id': x['org'], 'value': x['org']}, orgs))

    def has_access_to_user(self, user):
        ##own profile
        if user.id == self.id:
            return True
        elif self.is_superuser:
            return True
        elif self.is_admin() and (not user.is_superuser):
            return True
        elif user.parent is not None and self.id == user.parent.id:
            return True
        return False

class ProductUserRel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    cost = models.IntegerField("Стоимость продукта",)
    moddate = models.DateTimeField("Дата модификации связи", auto_now=True)
    adddate = models.DateTimeField("Дата добавления связи", auto_now_add=True)
    user_mod = models.IntegerField("Пользователь, который последний раз модифицировал запись",)
    class Meta:
        unique_together = ('user', 'product')

class OrderStatus(models.Model):
    code = models.CharField("Код статуса", max_length = 1, primary_key = True)
    name = models.CharField("Название статуса", max_length = 10, null=True)

    def is_in_progress(self):
        return self.code == 'I'
    def is_approved(self):
        return self.code == 'A'
    def is_rejected(self):
        return self.code == 'R'

    @staticmethod
    def get_all_statuses():
        statuses = OrderStatus.objects.all().values('code', 'name').order_by('code')
        return list(map(lambda x: { 'id': x['code'], 'value': x['name']}, statuses))

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Пользователь сделавший заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Заказанный продукт")
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, default='I', verbose_name="Статус")
    adddate = models.DateTimeField("Дата добавления заказа", auto_now_add=True)
    comment = models.TextField("Комментарий к заказу", null=True)
    codes = models.TextField("Коды активации", null=True)
    admin_comment = models.TextField("Ответ от администратора", null=True)
    amount = models.IntegerField("Количество")
    cost = models.IntegerField("Итоговая стоимость для одного продукта")

    @staticmethod
    def assign_status(id, status, comment, codes):
      try:
          new_status = OrderStatus.objects.get(code=status);
          try:
            order = Order.objects.get(id=id)
            if order.status.is_in_progress() and not new_status.is_in_progress():
                order.status = new_status
                if comment is not None and len(comment) > 0:
                    order.admin_comment = comment
                if codes is not None and len(codes) > 0:
                    order.codes = codes
                order.save()
          except Order.DoesNotExist:
            pass
      except OrderStatus.DoesNotExist:
          pass

    @staticmethod
    def get_orders(user, date_from=None, date_to=None, status_code=None, org=None, user_id=None):
      if user.is_admin() or user.is_superuser:
          orders = Order.objects.all().annotate(user_role=F('user__groups__name')).filter(adddate__range=[date_from, date_to])
          if org is not None and org != '*':
              orders = orders.filter(user__org=org)
      elif user.is_manager():
          orders = Order.objects.all().annotate(user_role=F('user__groups__name')).filter(Q(user__parent=user) | Q(user=user)).filter(adddate__range=[date_from, date_to])
          if user_id is not None and user_id != '*':
            if int(user_id) > 0:
                orders = orders.filter(user__id=int(user_id))
      else:
          orders = Order.objects.all().annotate(user_role=F('user__groups__name')).filter(user=user).filter(adddate__range=[date_from, date_to])
      if status_code is not None and status_code != '*':
          orders = orders.filter(status=status_code)
      return orders.order_by('-adddate')

    @staticmethod
    def get_order_codes(user, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if user.is_user() and order.user.id == user.id:
                return order.codes
            if user.is_manager() and (order.user.id == user.id or order.user.parent.id == user.id):
                return order.codes
            if user.is_admin() or user.is_superuser:
                return order.codes
            return ''
        except Order.DoesNotExist:
            return ''
