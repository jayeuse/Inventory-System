from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),

    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<str:order_id>/approve/', views.order_approve, name='order_approve'),
    path('orders/<str:order_id>/receive/', views.order_receive, name='order_receive'),
    path('orders/<str:order_id>/cancel/', views.order_cancel, name='order_cancel'),
    path('orders/list/', views.order_list, name='order_list'),
]