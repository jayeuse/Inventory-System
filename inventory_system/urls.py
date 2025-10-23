from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path, include
from . import views


router = DefaultRouter()

router.register(r'categories', views.CategoryViewSet)
router.register(r'subcategories', views.SubcategoryViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'product-stocks', views.ProductStocksViewSet)
router.register(r'product-batches', views.ProductBatchViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order-items', views.OrderItemViewSet)
router.register(r'receive-orders', views.ReceiveOrderViewSet)
router.register(r'transactions', views.TransactionViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard_view, name = 'dashboard'),
    path('products/', views.products_view, name = 'products'),
    path('inventory/', views.inventory_view, name = 'inventory'),
    path('transactions/', views.transactions_view, name = 'transactions'),
    path('settings/', views.settings_view, name = 'settings'),
    path('api/', include(router.urls)),
]