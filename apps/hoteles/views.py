from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hotel
from .serializers import HotelSerializer
from suscripciones.service import get_subscription

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    
class MySubscriptionView(APIView):
    def get(self, request):
        sub = get_subscription(request.tenant)
        return Response({
            "plan":sub.plan.nombre,
            "status": sub.status,
            "fin_periodo": sub.fin_periodo,
        }
            
        )