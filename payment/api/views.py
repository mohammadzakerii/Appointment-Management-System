from appointment.models import Appointment
from rest_framework import generics
from django.shortcuts import get_object_or_404
from .serializers import PayDownPaymentSerializer,DownPaymentResponseSerializer, VerifyPaymentSerializer, VerifyPaymentResponseSerializer, PaymentSerializer
from payment.services import ZarinPalService
from rest_framework.response import Response
from appointment.models import Payment
from rest_framework.permissions import AllowAny
from permissions.permissions import IsAdmin
from appointment.api.paginations import SmallResultSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from permissions.permissions import OwnerDoctorOrAdmin,OwnerPatientOrAdmin
from rest_framework.filters import SearchFilter
from django.shortcuts import get_object_or_404

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
    queryset=Payment.objects.all().order_by("-created_at")
    serializer_class = PaymentSerializer
    permission_classes = [IsAdmin]
    pagination_class = SmallResultSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["is_paid"]
    search_fields = ["name_of_doctor", "name_of_patient", "created_at"]

# create a view to retrieve individual payment related to specific appointment
class Payment_specific_appointment(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    # permission_classes = [OwnerDoctorOrAdmin]

    def get_object(self):
        appointment_id = self.kwargs.get("appointment_id")

        payment_obj = get_object_or_404(Payment, appointment_id = appointment_id)

        self.check_object_permissions

        return payment_obj

#create a view to get access to list of payment related to specific doctor             
class payment_specific_doctor(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [OwnerDoctorOrAdmin]
    pagination_class = SmallResultSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = {
        "created_at":["exact", "date","year"]
    }
    search_fields = ["appointment__patient__user__fullname"]  


    def get_queryset(self):
        doctor_id = self.kwargs.get("doctor_id")
        return Payment.objects.filter(appointment__doctor = doctor_id).all().order_by("-created_at")

#create a view to get access to list of payment related to specific patient
class payment_specific_patient(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [OwnerPatientOrAdmin]
    pagination_class = SmallResultSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["appointment__doctor__user__fullname"]
    filterset_fields = {"created_at":["exact", "date","year"]}    

    def get_queryset(self):
        patient_id = self.kwargs.get("patient_id")
        return Payment.objects.filter(appointment__patient_id=patient_id).all().order_by("-created_at")    


    

             
