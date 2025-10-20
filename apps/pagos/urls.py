from django.urls import path
from .views import PagoCreateAPIView, PagoListAPIView, PagoDetailAPIView

urlpatterns = [
    path('pagos/', PagoCreateAPIView.as_view(), name='pago-create'),
    path('pagos/list/', PagoListAPIView.as_view(), name='pago-list'),
    path('pagos/<int:pk>/', PagoDetailAPIView.as_view(), name='pago-detail'),
]
