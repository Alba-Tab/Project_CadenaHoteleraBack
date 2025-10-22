from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.pagos.models import Pago
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import PagoCreateSerializer
from apps.fidelizacion.models import CuentaFidelizacion


class PagoCreateAPIView(APIView):
    def post(self, request):
        serializer = PagoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pago = serializer.save()

        folio = pago.folio_estancia #type:ignore
        
        cliente = folio.reserva.huesped
        cuenta_fidelizacion = CuentaFidelizacion.objects.filter(cliente=cliente).first()
        
        response_data = {
            "pago": {
                "id": pago.id,#type:ignore
                "estado": pago.estado,#type:ignore
                "monto": str(pago.monto),#type:ignore
                "metodo": pago.metodo,#type:ignore
                "fecha_pago": str(pago.fecha_pago),#type:ignore
                "referencia": pago.referencia,#type:ignore
                "folio_id": folio.id,
            },
            "folio": {
                "id": folio.id,
                "estado": folio.estado,
                "total_pagado": str(folio.total_pagado),
                "reserva_total": str(folio.reserva.total),
                "pendiente": "0.00",
            }
        }
        
        if cuenta_fidelizacion:
            fidelizacion_info = {
                "puntos_acumulados": cuenta_fidelizacion.puntos_acumulados,
                "programa": cuenta_fidelizacion.fidelizacion.nombre,
                "puntos_ganados_este_pago": int(float(pago.monto))#type:ignore
            }
            
            # Si se aplicó descuento, incluir esa información
            if hasattr(pago, '_descuento_aplicado') and pago._descuento_aplicado > 0:#type:ignore
                fidelizacion_info["descuento_aplicado"] = str(pago._descuento_aplicado)#type:ignore
                fidelizacion_info["puntos_canjeados"] = pago._puntos_canjeados#type:ignore
                fidelizacion_info["monto_original"] = str(float(pago.monto) + float(pago._descuento_aplicado))#type:ignore
            
            response_data["fidelizacion"] = fidelizacion_info
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    

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
