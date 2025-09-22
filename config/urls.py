"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing_page'),

    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<str:order_id>/approve/', views.order_approve, name='order_approve'),
    path('orders/<str:order_id>/receive/', views.order_receive, name='order_receive'),
    path('orders/<str:order_id>/cancel/', views.order_cancel, name='order_cancel'),
    path('orders/list/', views.order_list, name='order_list'),
]
