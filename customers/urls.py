from rest_framework.routers import DefaultRouter
from .views import ClientViewSet

router = DefaultRouter()
router.register("tenants", ClientViewSet, basename="tenant")

urlpatterns = router.urls
