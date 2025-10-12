from rest_framework.routers import DefaultRouter

from django.urls import path, include
from . import views

router = DefaultRouter()

router.register(r'categories', views.CategoryViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'product-batches', views.ProductBatchViewSet)
router.register(r'order-items', views.OrderItemViewSet)
router.register(r'orders', views.OrderViewSet)


urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('api/', include(router.urls)),
]