from rest_framework.routers import DefaultRouter

from apps.reservas.views import ReservaViewSet

router = DefaultRouter()
router.register(r'', ReservaViewSet, basename='reservas')

urlpatterns = router.urls