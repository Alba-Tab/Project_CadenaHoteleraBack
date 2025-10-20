from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.pagos.models import Pago
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import PagoCreateSerializer


class PagoCreateAPIView(APIView):
    def post(self, request):
        serializer = PagoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pago = serializer.save()

        folio = pago.folio_estancia
        return Response({
            "pago": {
                "id": pago.id,
                "estado": pago.estado,
                "monto": str(pago.monto),
                "metodo": pago.metodo,
                "fecha_pago": str(pago.fecha_pago),
                "referencia": pago.referencia,
                "folio_id": folio.id,
            },
            "folio": {
                "id": folio.id,
                "estado": folio.estado,
                "total_pagado": str(folio.total_pagado),
                "reserva_total": str(folio.reserva.total),
                "pendiente": "0.00",
            }
        }, status=status.HTTP_201_CREATED)
    

class PagoListAPIView(ListAPIView):
    """
    GET /api/pagos/list/
    Retorna todos los pagos realizados.
    """
    queryset = Pago.objects.all().order_by('-fecha_pago')
    serializer_class = PagoCreateSerializer


class PagoDetailAPIView(RetrieveAPIView):
    """
    GET /api/pagos/<id>/
    Retorna el detalle de un pago específico.
    """
    queryset = Pago.objects.all()
    serializer_class = PagoCreateSerializer
