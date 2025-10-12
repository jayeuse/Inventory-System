from rest_framework import serializers
from .models import Supplier, Category, Product, ProductBatch

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'category_id',
            'category_name',
            'category_description',
            'product_count'
        ]

    def get_product_count(self, obj):
        return obj.product_set.count()

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'supplier_id',
            'supplier_name',
            'contact_person',
            'email',
            'phone_number',
            'address',
        ]

class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(source='category.category_name', read_only=True)
    class Meta:
        model = Product
        fields = [
            'product_id',
            'product_name',
            'category_id',
            'category_name',
            'sku',
            'price_per_unit',
            'last_update',
            'expiry_threshold_days',
            'low_stock_threshold',
        ]

class ProductBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBatch
        fields = [
            'batch_id',
            'product',
            'on_hand',
            'reserved',
            'expiry_date',
            'status',
        ]