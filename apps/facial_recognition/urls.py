from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacialRecognitionViewSet

router = DefaultRouter()
router.register(r'facial-recognition', FacialRecognitionViewSet, basename='facial-recognition')

urlpatterns = [
    path('', include(router.urls)),
]
