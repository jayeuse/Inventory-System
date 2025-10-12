from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Category

def update_product_count(category):
    count = category.products.count()
    print(f"Updating category {category.category_name}: {category.product_count} -> {count}")
    category.product_count = count
    category.save(update_fields=['product_count'])

@receiver(post_save, sender=Product)
def update_count_on_save(sender, instance, **kwargs):
    print(f"Signal triggered: Product {instance.product_name} saved")
    update_product_count(instance.category)

@receiver(post_delete, sender=Product)
def update_count_on_delete(sender, instance, **kwargs):
    print(f"Signal triggered: Product {instance.product_name} deleted")
    update_product_count(instance.category)