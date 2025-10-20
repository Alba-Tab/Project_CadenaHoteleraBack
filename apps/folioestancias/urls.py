from rest_framework.routers import DefaultRouter

from .views import FolioEstanciaViewSet

router = DefaultRouter()
router.register(r'', FolioEstanciaViewSet, basename='folioestancia')

urlpatterns = router.urls