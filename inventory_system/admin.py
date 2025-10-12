from django.contrib import admin
from .models import (
    Product, ProductBatch, Order, OrderItem,
    Dispense, DispenseItem, Transaction,
    Category, Supplier
)

admin.site.register(Product)
admin.site.register(ProductBatch)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Dispense)
admin.site.register(DispenseItem)
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Supplier)
