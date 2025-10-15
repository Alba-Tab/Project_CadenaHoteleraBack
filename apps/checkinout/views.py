from django.shortcuts import render
from rest_framework import viewsets
from .models import CheckInOut
from .serializers import CheckInOutSerializer
from rest_framework.permissions import AllowAny

class CheckInOutViewSet(viewsets.ModelViewSet):
    queryset = CheckInOut.objects.all()
    serializer_class = CheckInOutSerializer
    permission_classes = [AllowAny]
