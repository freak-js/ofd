from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Q

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

class OrderStatus(models.Model):
    code = models.CharField("Код статуса", max_length = 1, primary_key = True)

    def is_in_progress(self):
        return self.code == 'I'
    def is_approved(self):
        return self.code == 'A'
    def is_rejected(self):
        return self.code == 'R'

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Номер заказа")
    products = models.ManyToManyField(Product, through="OrderProduct", verbose_name="Продукты заказанные пользователем")
    adddate = models.DateTimeField("Дата добавления заказа", auto_now_add=True)
    comment = models.TextField("Комментарий к заказу", null=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, default='I', verbose_name="Статус")

    #FILTER_DATE_FROM_KEY = 'date_from'
    #FILTER_DATE_TO_KEY   = 'date_to'
    #FILTER_STATUS_KEY    = 'status'
    #FILTER_KEYS          = [FILTER_DATE_FROM_KEY, FILTER_DATE_TO_KEY, FILTER_STATUS_KEY]

    #@staticmethod
    #def get_order_filters():
    #    return FILTER_KEYS

    #@staticmethod
    #def get_order_filter_key():
    #    return 'orders_filter'

    @staticmethod
    def assign_status(ids, status):
      try:
          new_status = OrderStatus.objects.get(code=status);
          for id in ids:
              try:
                  order = Order.objects.get(id=id)
                  if order.status.is_in_progress() and not new_status.is_in_progress():
                      order.status = new_status
                      order.save()
              except Order.DoesNotExist:
                  pass
      except OrderStatus.DoesNotExist:
          pass

    @staticmethod
    def get_orders(user, date_from=None, date_to=None, status_code=None):
      if user.is_admin() or user.is_superuser:
          #orders = Order.objects.all()
          orders = Order.objects.all().filter(adddate__range=[date_from, date_to])
      elif user.is_manager():
          #orders = Order.objects.all().filter(order__user__parent=user)
          orders = Order.objects.all().filter(Q(user__parent=user) | Q(user=user)).filter(adddate__range=[date_from, date_to])
      else:
          #orders = Order.objects.all().filter(user=user)
          orders = Order.objects.all().filter(user=user).filter(adddate__range=[date_from, date_to])
      if status_code is not None:
          try:
              status = OrderStatus.objects.get(code=status);
              orders.filter(status=status)
          except OrderStatus.DoesNotExist:
              pass
      return orders

    #@staticmethod
    #def apply_default_filters(session, order):
    #    session[FILTER_KEY][FILTER_DATE_FROM_KEY] = datetime.date.today()
    #    session[FILTER_KEY][FILTER_DATE_TO_KEY] = session[FILTER_KEY][FILTER_DATE_FROM_KEY] + datetime.timedelta(1)
    #    order.filter(adddate=[session[FILTER_KEY][FILTER_DATE_FROM_KEY], session[FILTER_KEY][FILTER_DATE_TO_KEY]])

    #@staticmethod
    #def apply_filters(session, orders):
    #    session_key = get_order_filter_key()
    #    if session_key in session:
    #        pass
    #    else:
    #        apply_default_filters(session)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name="Отношение к номеру заказа")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Отношение к продукту")
    amount = models.IntegerField("Количество")
    cost = models.IntegerField("Итоговая стоимость для одного продукта")
