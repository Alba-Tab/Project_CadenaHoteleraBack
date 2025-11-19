from rest_framework.routers import DefaultRouter
from .views import BackupViewSet

router = DefaultRouter()
router.register("", BackupViewSet, basename="backup")  # ✅ Cambiado de "backups" a ""

urlpatterns = router.urls
