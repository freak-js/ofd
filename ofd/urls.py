"""ofd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ofd_app import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='ofd_app/index.html', redirect_authenticated_user=True), name="login"),
    path('login/', auth_views.LoginView.as_view(template_name='ofd_app/index.html', redirect_authenticated_user=True), name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name="logout"),
    path('product/', views.product, name='product'),
    path('product/<int:id>/', views.product, name='product'),
    path('products/', views.products, name='products'),
    path('products/delete', views.product_delete, name='product_delete'),
    path('user/', views.user, name='user'),
    path('users/', views.users, name='users'),
    path('user/<int:id>/', views.user, name='user'),
    path('user/delete', views.user_delete, name='user_delete'),
    path('user_product/<int:id>/', views.user_product, name='user_product'),
    path('reg/', views.user_reg, name='user_reg'),
    #path('basket/', views.get_basket, name='basket'),
    path('orders/', views.orders, name='orders'),
    path('stat_org/', views.stat_org, name='stat_org'),
    path('orders/exportxlsx/<int:id>/', views.exportxlsx, name='exportxlsx'),
    path('orders/exporttxt/<int:id>/', views.exporttxt, name='exporttxt'),
    path('feedback/', views.feedback, name='feedback'),
    path('instruction/', views.instruction, name='instruction'),

]
