from django.urls import path
from .views import CheckInCreateAPIView, CheckoutAPIView, CheckInListAPIView, CheckInDetailAPIView

urlpatterns = [
    path('checkin/', CheckInCreateAPIView.as_view(), name='checkin-create'),
    path('checkout/<int:reserva_id>/', CheckoutAPIView.as_view(), name='checkout'),
     path('list/', CheckInListAPIView.as_view(), name='checkin-list'),
    path('<int:pk>/', CheckInDetailAPIView.as_view(), name='checkin-detail'),
    path('reportes/', include('apps.checkinout.reportes.urls')),
]