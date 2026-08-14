from rest_framework import serializers
from appointment.models import Service, WorkingHour, Appointment, Payment
from account.models import Doctor
from datetime import timezone 
import datetime
from django.shortcuts import get_object_or_404
from appointment.api.utils import slot_generator
from django.db import transaction
from decimal import Decimal

class ServiceSerializer(serializers.ModelSerializer):
    name_of_doctor = serializers.CharField(source = "doctor.user.fullname", read_only=True)
    doctor_specialization =serializers.CharField(source="doctor.specialization", read_only = True)

    class Meta:
        model = Service
        fields = ["name", "price", "slot_duration", "name_of_doctor", "doctor_specialization", "doctor"]
        read_only_fields = ["name_of_doctor" ]
        extra_kwargs = {
            "doctor": {"required": False}
        }

    def validate(self, attrs):
           request = self.context["request"]
           if request.user.role == "doctor" and "doctor" in attrs:
               raise serializers.ValidationError("doctor cant set doctor field")
           return attrs
                
class WorkingHourSerializer(serializers.ModelSerializer):
    name_of_doctor = serializers.CharField(source = "doctor.user.fullname", read_only=True)

    class Meta:
        model = WorkingHour
        fields =["start_work_time", "end_work_time", "doctor","days_of_week", "name_of_doctor"]
        read_only_fields = ["name_of_doctor"]
        extra_kwargs = {
            "doctor":{"required": False}
        }  

    def validate(self, attrs):
        request = self.context["request"]

        if request.user.role == "doctor":

            if "doctor" in attrs:
                raise serializers.ValidationError({
                    "doctor": "Doctor cannot specify doctor field."
                })

            
            attrs["doctor"] = request.user.doctor   

        elif request.user.role == "admin":

            if not attrs.get("doctor"):
                raise serializers.ValidationError({
                    "doctor": "Admin must specify doctor."
                })

        else:
            raise serializers.ValidationError("you dont have permission")     

        if WorkingHour.objects.filter(doctor = attrs["doctor"], days_of_week = attrs["days_of_week"]).exists():
            raise serializers.ValidationError("a working hour in this day of week has been set before")       

        return attrs    

class workinghourDetailSerializer(serializers.ModelSerializer):
    name_of_doctor = serializers.CharField(source = "doctor.user.fullname", read_only=True)
    
    class Meta:
        model = WorkingHour
        fields =["start_work_time", "end_work_time", "doctor","days_of_week", "name_of_doctor"]
        read_only_fields = ["name_of_doctor"]
        extra_kwargs = {
        "doctor":{"required": False}
        }

    def validate(self, attrs):
        request = self.context["request"]
        if "days_of_week" in attrs:
            if WorkingHour.objects.filter(days_of_week=attrs["days_of_week"], doctor=request.user.doctor).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("you have another working hour on this day of week")

        return attrs    


         

class CreateAppointmentSerializer(serializers.Serializer):
    date = serializers.DateField()
    start_time = serializers.TimeField()

    def validate_date(self, value):
        if value < datetime.date.today():
            raise serializers.ValidationError("date cant be in the past")
        return value
    
   
    def validate(self, attrs):
        date = attrs["date"]
        start_time = attrs["start_time"]
        service= self.context["service"]
        doctor =  self.context["doctor"]
        patient = self.context["patient"]
        
        day_of_week = date.weekday()

        #check if any other appontments created at this time befor
        if Appointment.objects.filter(date = date, doctor=doctor, start_time=start_time).exists():
            raise serializers.ValidationError("this time already booked")

        #check if patient has booked the same appontment one time on this date
        if Appointment.objects.filter(date=date, patient=patient).exists():
            raise serializers.ValidationError("you booked one time for this date")
        
        try:
            workinghour = WorkingHour.objects.get(doctor=doctor, days_of_week = day_of_week)
        except WorkingHour.DoesNotExist:
            raise serializers.ValidationError("doctor doesnt work on this date")
            
        generated_slots = slot_generator(workinghour.start_work_time, workinghour.end_work_time, service.slot_duration)
        if start_time not in generated_slots:
            raise serializers.ValidationError("invalid time")
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            service = self.context["service"]
            doctor = self.context["doctor"]
            patient =self.context["patient"]

            date = validated_data["date"]
            start_time = validated_data["start_time"]

            new_appointment = Appointment.objects.create(date=date, doctor=doctor, patient=patient, start_time=start_time,service=service, status="scheduled")
            Payment.objects.create(appointment = new_appointment, amount_to_pay = new_appointment.service.price ,down_payment =new_appointment.service.price * Decimal("0.2"), remaining_amount = new_appointment.service.price)
            return new_appointment

        


class AppointmentSerializer(serializers.ModelSerializer):
    name_of_doctor = serializers.CharField(source= "doctor.user.fullname", read_only=True)
    name_of_patient = serializers.CharField(source="patient.user.fullname", read_only=True)
    name_of_service = serializers.CharField(source="service.name", read_only=True)
    down_payment = serializers.DecimalField(source = "payment.down_payment",max_digits=10, decimal_places=3, read_only = True)
    remaining_amount = serializers.DecimalField(source="payment.remaining_amount",max_digits=10, decimal_places=3, read_only=True)
    is_paid = serializers.BooleanField(source="payment.is_paid", read_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"


class DoctorSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="user.fullname", read_only=True)
    class Meta:
        model = Doctor
        fields = [
            "id",
            "doctor_name",
            "specialization"
        ]

    
    
class DoctorDateSerializer(serializers.Serializer):
    date = serializers.DateField()

    def validate_date(self, value):
        if value < datetime.date.today():
            raise serializers.ValidationError("you cant choose the past date")
        return value

class GetAvailableSlotsSerializer(serializers.Serializer):
    date= serializers.DateField()

    def validate_date(self, value):
        if value < datetime.date.today():
            raise serializers.ValidationError("date cant be in the past")
        return value
    
    def get_available_slots(self):
        service = self.context["service"]
        doctor = self.context["doctor"]
        date = self.validated_data["date"]
        day = date.weekday()
        try:
            workinghour = WorkingHour.objects.get(doctor=doctor, days_of_week=day)
        except WorkingHour.DoesNotExist:
            raise serializers.ValidationError("doctor doesnt work on this day")
        generated_slots = slot_generator(workinghour.start_work_time, workinghour.end_work_time, service.slot_duration)
        booked_slots = Appointment.objects.filter(doctor=doctor, date=date).exclude(status="canceled").values_list("start_time", flat=True)
        available_slots =[slot for slot in generated_slots if slot not in booked_slots] 
        return {
            "slots":available_slots,
            "doctor_name":doctor.user.fullname,
            "day_name":workinghour.get_days_of_week_display()
        }

class AvailableSlotResponseSerializer(serializers.Serializer):
    date = serializers.DateField()
    doctor_name= serializers.CharField()
    day_name = serializers.CharField()
    slots = serializers.ListField(child= serializers.TimeField())

class AppointmentResponseSerializer(serializers.ModelSerializer):
   amount_to_pay = serializers.DecimalField(source="payment.amount_to_pay", read_only=True, max_digits=10, decimal_places=3)
   remaining_amount = serializers.DecimalField(source= "payment.remaining_amount", read_only = True,  max_digits=10, decimal_places=3)
   down_payment = serializers.DecimalField(source = "payment.down_payment", read_only=True, max_digits=10, decimal_places = 3)
   id_paid = serializers.BooleanField(source = "paument.is_pad", read_only = True) 
   doctor_name = serializers.CharField(source = "doctor.user.fullname", read_only=True)
   patient_name = serializers.CharField(source = "patient.user.fullname", read_only=True)
   service_name = serializers.CharField(source="service.name", read_only=True)

   class Meta:
       model = Appointment
       fields  = [ "id", "doctor","patient","down_payment" ,"status", "amount_to_pay", "id_paid", "service", "date", "start_time", "doctor_name", "patient_name", "service_name","remaining_amount"]

class CanceleAppontmentSerializer(serializers.Serializer):

    def save(self, *args, **kwarg):
        appointment = self.context["appointment"]
        with transaction.atomic():
            if appointment.status == "completed":
                raise serializers.ValidationError("completed appointment cant be canceled")

            if appointment.status == "canceled":
                raise serializers.ValidationError("this appointment has alraedy been canceled")
            else:
                appointment.status = "canceled"
                appointment.save(update_fields=["status"])
                
                return {
                    "message":"appointment canceled successfully",
                    "doctor_name":appointment.doctor.user.fullname,
                    "patient_name":appointment.patient.user.fullname,
                    "start_time":appointment.start_time,
                    "service":appointment.service.name,
                    "status":appointment.status
                        }

class CanceleAppontmnetResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    doctor_name = serializers.CharField()
    patient_name = serializers.CharField()
    start_time = serializers.TimeField()
    service = serializers.CharField()
    status = serializers.CharField()      

class PayDownPaymentSerializer(serializers.Serializer):
    down_payment = serializers.DecimalField(max_digits=10, decimal_places=3)

    def validate_down_payment(self, value):
        appointment = self.context["appointment"]
        if value != appointment.payment.down_payment:
            raise serializers.ValidationError("entered price not equal to price of down payment")
        return value
    
    def pay_down_payment(self):
        appointment = self.context["appointment"]
        down_payment = self.validated_data["down_payment"]
        
        appointment.payment.is_paid=True
        appointment.payment.remaining_amount = appointment.service.price - down_payment
        appointment.payment.down_payment = appointment.payment.down_payment - down_payment
        appointment.payment.save(update_fields=["down_payment", "is_paid", "remaining_amount"])
        return {
            "down_payment":appointment.payment.down_payment,
            "is_paid":appointment.payment.is_paid,
            "remaining_amount":appointment.payment.remaining_amount}
    
class PayDownPaymentResponseSerializer(serializers.Serializer):
    down_payment = serializers.DecimalField(max_digits=10, decimal_places=3)
    is_paid = serializers.BooleanField()
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=3)   

#create a view to insert information of pay reciet  in doctor offic     
class CompleteAppointmentSerializer(serializers.Serializer):
    final_payment = serializers.DecimalField(max_digits=10, decimal_places=3)
    ref_id = serializers.CharField(min_length=4, max_length=4)
    card_num = serializers.CharField(min_length=4, max_length=4)

    def validate_ref_id(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("ref_id only cantains numeric characters")
        return value

    def validate_card_num(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("cart number only cantains numeric characters")
        return value
    
    def validate(self, attrs):
        appointment = self.context["appointment"]

        if not appointment.payment.is_paid:
            raise serializers.ValidationError("down payment hasnt been paid")
        
        if appointment.status == "completed":
            raise serializers.ValidationError("appointment already completed")
        
        return attrs
        
    
    def save(self, **kwargs):
        appointment = self.context["appointment"]
        final_payment = self.validated_data["final_payment"]
        ref_id = self.validated_data["ref_id"]
        card_num =self.validated_data["card_num"]

        with transaction.atomic():
            appointment.payment.remaining_amount -=  final_payment
            appointment.payment.ref_id = ref_id
            appointment.payment.card_num = card_num
            appointment.payment.save(update_fields=["remaining_amount", "ref_id", "card_num"])
            if appointment.payment.remaining_amount == 0:
                appointment.status = "completed"
                appointment.save(update_fields = ["status"])
            return appointment

  

