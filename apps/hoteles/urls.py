from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, MySubscriptionView

router = DefaultRouter()
router.register('hoteles', HotelViewSet, basename='hotel') 
router.register('Mi-suscripcion', MySubscriptionView, basename='hotel') 


urlpatterns = [
    path('', include(router.urls)),
    path('reportes/', include('apps.hoteles.reportes.urls')),
]