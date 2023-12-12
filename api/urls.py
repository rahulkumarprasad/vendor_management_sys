from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorViewSet, PurchaseOrderViewSet, VendorPerformance, PurchaseOrderAck
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()

router.register("vendors", VendorViewSet)
router.register("purchase_orders", PurchaseOrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("vendors/<str:vendor_id>/performance", VendorPerformance.as_view(), name="vendors_performance"),
    path("purchase_orders/<str:pk>/acknowledge", PurchaseOrderAck.as_view(), name="purchase_order_ack"),

    #token api
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]