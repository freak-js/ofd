# Used for top menu navigation
PRODUCTS = 'products'
USERS = 'users'
ORDERS = 'orders'
MY_CARD = 'my_card'
STAT = 'stat'

#Template registered user

TEMPLATE_EMAIL_NEW_LOGIN_USER_SUBJECT = 'Добро пожаловать {first_name} !'
TEMPLATE_EMAIL_NEW_LOGIN_USER_BODY = 'Вы успешно зарегестрировались на платформе mir-ofd.ru - как {login}. Наш менеджер свяжится с вами в ближайшее время.'

#Template admin

TEMPLATE_EMAIL_NEW_LOGIN_ADMIN_SUBJECT = 'Новый пользователь!'
TEMPLATE_EMAIL_NEW_LOGIN_ADMIN_BODY = 'Пользователь {first_name} {last_name} почта:{email} телефон:{phone_number} организация: {org} город: {city} только что успешно зарегестрировался.'

#Template new order user

TEMPLATE_EMAIL_NEW_ORDER_USER_SUBJECT = 'Вы успешно оформили заказ.'
TEMPLATE_EMAIL_NEW_ORDER_USER_BODY = 'Заказ № {number} от {date} на сумму {total} на {product} в количестве {amount} шт. успешно оформлен. В скором времени он будет обработан.'

#Template new order admin

TEMPLATE_EMAIL_NEW_ORDER_ADMIN_SUBJECT = 'У нас новый заказ.'
TEMPLATE_EMAIL_NEW_ORDER_ADMIN_BODY = 'Пользователь {first_name} {last_name} из организации {corg} оформил заказ на {product} в количестве {amount} на сумму {total}'

#Template change order status user

TEMPLATE_EMAIL_ORDER_STATUS_USER_SUBJECT = 'Статус заказа изменен.'
TEMPLATE_EMAIL_ORDER_STATUS_USER_BODY = 'Статус заказа № {number} от {date} на сумму {total} на {product} в количестве {amount} шт. изменен на {status}. Комментарий администратора: {comment}'

##MESSAGES##

MESSAGES = {}
MESSAGES[1] = 'Отклонён'
MESSAGES[2] = 'Завершён'

