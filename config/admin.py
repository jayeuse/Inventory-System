from django.contrib import admin
from inventory_system.models import (
    Product, ProductBatch, Order, OrderItem,
    Dispense, DispenseItem, Transaction,
    Category, Location, Supplier
)

admin.site.register(Product)
admin.site.register(ProductBatch)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Dispense)
admin.site.register(DispenseItem)
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Supplier)
