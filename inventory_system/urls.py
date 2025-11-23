from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path, include
from . import views
from . import auth_views


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
router.register(r'archive_logs', views.ArchiveLogViewSet)
router.register(r'users', views.UserInformationViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name = 'dashboard'),
    path('products/', views.products_view, name = 'products'),
    path('inventory/', views.inventory_view, name = 'inventory'),
    path('transactions/', views.transactions_view, name = 'transactions'),
    path('settings/', views.settings_view, name = 'settings'),
    
    # Authentication API endpoints
    path('api/auth/login/', auth_views.login_api, name='api_login'),
    path('api/auth/verify-otp/', auth_views.verify_otp, name='verify_otp'),
    path('api/auth/resend-otp/', auth_views.resend_otp, name='resend_otp'),
    path('api/auth/logout/', auth_views.logout_api, name='api_logout'),
    path('api/auth/me/', auth_views.current_user, name='current_user'),
    
    # Password Reset API endpoints
    path('api/auth/check-username/', auth_views.check_username, name='check_username'),
    path('api/auth/request-password-reset/', auth_views.request_password_reset, name='request_password_reset'),
    path('api/auth/verify-reset-otp/', auth_views.verify_reset_otp, name='verify_reset_otp'),
    path('api/auth/reset-password/', auth_views.reset_password, name='reset_password'),
    path('api/auth/resend-reset-otp/', auth_views.resend_reset_otp, name='resend_reset_otp'),
    
    # Dashboard aggregates
    path('api/dashboard/categories/', views.dashboard_categories, name='api_dashboard_categories'),
    path('api/dashboard/top-suppliers/', views.dashboard_top_suppliers, name='api_dashboard_top_suppliers'),
    path('api/dashboard/stock-status/', views.dashboard_stock_status, name='api_dashboard_stock_status'),
    path('api/dashboard/stats/', views.dashboard_stats, name='api_dashboard_stats'),

    path('api/', include(router.urls)),
]