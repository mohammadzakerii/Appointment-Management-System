from rest_framework import generics
from appointment.models import Service,WorkingHour, Appointment, Payment
from appointment.api.serializers import ServiceSerializer, WorkingHourSerializer, AppointmentSerializer,DoctorDateSerializer,DoctorSerializer, GetAvailableSlotsSerializer, AvailableSlotResponseSerializer, AppointmentValidatANDCreateSerializer, AppointmentResponseSerializer, PayDownPaymentSerializer, PayDownPaymentResponseSerializer, CompleteAppointmentSerializer, CanceleAppontmentSerializer, CanceleAppontmnetResponseSerializer
from appointment.api.permissions import IsDoctor, IsPatient, PatientOrAllowAny, DoctorOrAdmin
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework import status
from rest_framework.permissions import AllowAny
from datetime import timedelta, date
import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.response import Response
from django.http import JsonResponse
from appointment.utils import slot_generator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from account.models import User, Patient, Doctor
from django.db import transaction
import decimal
from .paginations import SmallResultSetPagination
from rest_framework.filters import SearchFilter

# the view below creates and returns list of services
class ServiceView(generics.ListCreateAPIView):
    queryest = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Service.objects.all()

#the view below retrieves, updates and removes an individual service object it requires permissions    
class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, IsDoctor]


    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            service_obj = Service.objects.get(pk=pk)
        except Service.DoesNotExist:
            raise NotFound("service doesnt exist")
        
        return service_obj

#this view creates a working hour object and returns list of working hour objects     
class WorkingHourView(generics.ListCreateAPIView):
    serializer_class = WorkingHourSerializer
    permission_classes = [IsAuthenticated]  
    pagination_class = SmallResultSetPagination
    filter_backends = [SearchFilter]
    search_fields =["doctor__user__fullname"]

    def get_queryset(self):
        return WorkingHour.objects.all() 

#the view below retrieves, updates and removes an individual objects by its id and it also needs permissions   
class WorkingHourDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkingHourSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            WorkingHour_obj = WorkingHour.objects.get(pk=pk)
        except WorkingHour.DoesNotExist:
            raise NotFound("working hour not found")
        
        return WorkingHour_obj
    

#this view returns all working hour objects related to an individual doctor
class WorkinghourOfSpecefiecDoctorView(generics.ListAPIView):
    serializer_class = WorkingHourSerializer
    permission_classes =[AllowAny]
    pagination_class = SmallResultSetPagination
    
    
    def get_queryset(self):
        pk = self.kwargs.get("pk")
        queryset = WorkingHour.objects.filter(doctor_id=pk)
        return queryset
    

# create a view to get access to all doctors working on specefiec date entered by client in query params  
class DoctorWorkingHourDate(generics.ListAPIView):
    serializer_class = DoctorSerializer
    
    def get_queryset(self):
        serializer = DoctorDateSerializer(data = self.request.query_params) 
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data.get("date")
        day = date.weekday()
        return Doctor.objects.filter(workinghour__days_of_week =day)   
        

#create a view to get acces to available time slot        
class GetAvailableSlots(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsPatient]
    serializer_class = GetAvailableSlotsSerializer

    def get(self, request, service_id):
        service = get_object_or_404(Service, pk=service_id)
        doctor = service.doctor
        serializer = self.get_serializer(data = request.query_params, context={"service":service, "doctor":doctor})
        serializer.is_valid(raise_exception = True)  
        available_slots = serializer.get_available_slots()
        response_serializer = AvailableSlotResponseSerializer({
            "date":serializer.validated_data["date"],
            **available_slots
            }) 
        return Response(response_serializer.data)        
    

class CreateAppointment(generics.CreateAPIView):
    serializer_class = AppointmentValidatANDCreateSerializer
    permission_classes = [IsAuthenticated,IsPatient]

    def get_serializer_context(self):
        context = super().get_serializer_context()

        service = get_object_or_404(Service, pk=self.kwargs["service_id"])
        context.update({
            "service":service,
            "doctor":service.doctor,
            "patient":self.request.user.patient
        })

        return context


    def create(self,request , *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        new_appointment = serializer.save()
        response_serializer = AppointmentResponseSerializer(new_appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)



#the view below returns a list of appointments   
class AppointmentList(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [AllowAny]
    pagination_class = SmallResultSetPagination
    filter_backends = [SearchFilter]
    search_fields = ["patient__user__fullname","doctor__user__fullname"]

#this view canceles appointment by its patient
class CancelAppointment(generics.GenericAPIView):
    serializer_class = CanceleAppontmentSerializer
    permission_classes = [IsAuthenticated, PatientOrAllowAny]

    with transaction.atomic():
        def patch(self , request, appointment_id):

            try:
                appointment = Appointment.objects.get(pk=appointment_id, patient_id = request.user.patient.id)
            except Appointment.DoesNotExist:
                return Response({"error":"appointment not found"})
                
            serializer = self.get_serializer(context={"appointment":appointment})
            

            result = serializer.save()
            response_serializer = CanceleAppontmnetResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        

#this view deletes entire object of appointment        
class DeleteAppointment(generics.DestroyAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated,DoctorOrAdmin]

    def get_object(self):
        appointment_id = self.kwargs.get("appointment_id")
        object = Appointment.objects.get(pk=appointment_id)
        return object

#this view returns list of appointments related to individual patient
class AppointmentListOfSpecefiecPatient(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        patient_id = self.kwargs.get("patient_id")
        queryset = Appointment.objects.filter(patient_id = patient_id)
        return queryset

      
#this view returns list of appointments related to individual doctor       
class AppointmentListOfSpecefiecDoctor(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [AllowAny]
    pagination_class = SmallResultSetPagination
    filter_backends = [SearchFilter]
    search_fields = ["name_of_doctor"]

    def get_queryset(self):
        doctor_id = self.kwargs.get("doctor_id")
        queryset = Appointment.objects.filter(doctor_id = doctor_id)
        return queryset

#create a view to pay remaining amount and complete the appointment   
class CompleteAppointment(generics.GenericAPIView):
    serializer_class = CompleteAppointmentSerializer
    permission_classes = [IsAuthenticated,DoctorOrAdmin]
    def get(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        return Response({"message":f"remainig amount is {appointment.payment.remaining_amount}"})

    def post(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, pk=appointment_id) 
        serializer = self.get_serializer(data = request.data, context={"appointment":appointment})
        serializer.is_valid(raise_exception=True)
        
        appointment_edited = serializer.save()
        response_serializer = AppointmentResponseSerializer(appointment_edited)
        return Response(response_serializer.data)
            


    

        








    











