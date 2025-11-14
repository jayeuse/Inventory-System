from django.contrib import admin
from .models import (
    Product, ProductBatch, Order, OrderItem, Transaction,
    Category, Supplier, OTP, UserInformation
)

admin.site.register(Product)
admin.site.register(ProductBatch)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Supplier)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp', 'created_at', 'expires_at', 'is_used', 'is_verified', 'is_valid_display']
    list_filter = ['is_used', 'is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'otp']
    readonly_fields = ['otp_code', 'created_at', 'expires_at']
    ordering = ['-created_at']
    
    def is_valid_display(self, obj):
        return obj.is_valid()
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Valid'


@admin.register(UserInformation)
class UserInformationAdmin(admin.ModelAdmin):
    list_display = ['user_info_id', 'user', 'role', 'phone_number', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number']
    readonly_fields = ['user_info_code', 'user_info_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
