from datetime import datetime, timezone

# Used for top menu navigation
PRODUCTS = 'products'
USERS = 'users'
ORDERS = 'orders'
MY_CARD = 'my_card'
STAT = 'stat'
FEEDBACK = 'feedback'
INSTRUCTION = 'instruction'

#Template registered user

TEMPLATE_EMAIL_NEW_LOGIN_USER_SUBJECT = 'Добро пожаловать, {first_name}!'
TEMPLATE_EMAIL_NEW_LOGIN_USER_BODY = 'Вы успешно зарегестрировались на платформе mir-ofd.ru - как {login}. Наш менеджер свяжится с вами в ближайшее время.'

#Template admin

TEMPLATE_EMAIL_NEW_LOGIN_ADMIN_SUBJECT = 'Новый пользователь!'
TEMPLATE_EMAIL_NEW_LOGIN_ADMIN_BODY = 'Пользователь: {first_name} {last_name} \nпочта: {email} \nтелефон: {phone_number} \nорганизация: {org} \nгород: {city}\n только что успешно зарегестрировался.'

#Template new order user

TEMPLATE_EMAIL_NEW_ORDER_USER_SUBJECT = 'Вы успешно оформили заказ.'
TEMPLATE_EMAIL_NEW_ORDER_USER_BODY = 'Заказ № {number} от {date} на сумму {total} р. на {product} в количестве {amount} шт. успешно оформлен. В скором времени он будет обработан.'

#Template new order admin

TEMPLATE_EMAIL_NEW_ORDER_ADMIN_SUBJECT = 'У нас новый заказ.'
TEMPLATE_EMAIL_NEW_ORDER_ADMIN_BODY = 'Пользователь: {first_name} {last_name} \nиз организации: {corg} \nоформил заказ на: {product} \nв количестве: {amount} шт. \nна сумму: {total} р.'

#Template change order status user

TEMPLATE_EMAIL_ORDER_STATUS_USER_SUBJECT = 'Статус заказа изменен.'
TEMPLATE_EMAIL_ORDER_STATUS_USER_BODY = 'Статус заказа № {number} от {date} на сумму {total} р. на {product} в количестве {amount} шт. изменен на {status}. \nКомментарий администратора: {comment}'

##MESSAGES##

MESSAGES = {}
MESSAGES[1] = 'Отклонён'
MESSAGES[2] = 'Завершён'

#Дата после которой будет работать функция выставления счета и УПД

DATE_AFTER_WHICH_INVOICES_WILL_BE_ISSUED = datetime(2019, 8, 30, 10, 10, 10).replace(tzinfo=timezone.utc).astimezone(tz=None)

