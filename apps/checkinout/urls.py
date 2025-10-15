from rest_framework.routers import DefaultRouter
from .views import CheckInOutViewSet

router = DefaultRouter()
router.register(r'', CheckInOutViewSet, basename='checkinout')

urlpatterns = router.urls
