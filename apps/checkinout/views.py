from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from apps.checkinout.models import CheckInOut
from apps.reservas.models import Reserva
from .serializers import CheckInCreateSerializer, CheckoutSerializer


class CheckInCreateAPIView(APIView):

    def post(self, request):
        serializer = CheckInCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        checkin = serializer.save()

        folio = checkin.reserva.folios_estancia.first()
        data = {
            "checkin": CheckInCreateSerializer(checkin).data,
            "folio": {
                "id": folio.id,
                "estado": folio.estado,
                "total_pagado": str(folio.total_pagado),
                "reserva_id": folio.reserva_id,
                "huesped_id": folio.huesped_id,
            },
        }
        return Response(data, status=status.HTTP_201_CREATED)


class CheckoutAPIView(APIView):
    def put(self, request, reserva_id: int):
        reserva = get_object_or_404(Reserva, pk=reserva_id)
        checkin = getattr(reserva, "checkinout", None)
        if not checkin:
            return Response({"detail": "La reserva no tiene check-in registrado."}, status=400)

        serializer = CheckoutSerializer(instance=checkin, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        checkin = serializer.save()
        return Response(CheckoutSerializer(checkin).data, status=200)


class CheckInListAPIView(ListAPIView):

    queryset = CheckInOut.objects.all().order_by('-fecha_checkin')
    serializer_class = CheckInCreateSerializer


class CheckInDetailAPIView(RetrieveAPIView):

    queryset = CheckInOut.objects.all()
    serializer_class = CheckInCreateSerializer
