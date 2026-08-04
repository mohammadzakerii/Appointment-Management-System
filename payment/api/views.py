from appointment.models import Appointment
from rest_framework import generics
from django.shortcuts import get_object_or_404
from .serializers import PayDownPaymentSerializer,DownPaymentResponseSerializer, VerifyPaymentSerializer, VerifyPaymentResponseSerializer, PaymentSerializer
from payment.services import ZarinPalService
from rest_framework.response import Response
from appointment.models import Payment
from rest_framework.permissions import AllowAny
from appointment.api.permissions import IsAdmin
from appointment.api.paginations import SmallResultSetPagination
from django_filters.rest_framework import DjangoFilterBackend


 #create a view to reqest to pay the down payment 
class PayDownPayment(generics.GenericAPIView):
    serializer_class = PayDownPaymentSerializer
    permission_classes = [AllowAny]
    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment,id=appointment_id)
        serializer = self.get_serializer(data = request.data, context = {"appointment":appointment})
        serializer.is_valid(raise_exception=True)
        result  =  serializer.save()
        response_serializer = DownPaymentResponseSerializer(result)
        return Response(response_serializer.data)

#create a view to verify payment 
class VerifyPayment(generics.GenericAPIView):
    queryset = Payment.objects.all()
    serializer_class = VerifyPaymentSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        
        data = {
            "authority":request.query_params["Authority"],
            "status":request.query_params["Status"]
                }
        serializer = self.get_serializer(data = data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()
        response_serializer = VerifyPaymentResponseSerializer(result)
        return Response(response_serializer.data)
         
#create a view to get access to a list of payments
class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAdmin]
    pagination_class = SmallResultSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_paid"]

    def get_queryset(self):
        return Payment.objects.all()
    
    

             
