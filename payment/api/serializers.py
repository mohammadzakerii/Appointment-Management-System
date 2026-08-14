from rest_framework import serializers
from payment.services import ZarinPalService
from django.conf import settings
from rest_framework.response import Response
from appointment.models import Payment
from django.shortcuts import get_object_or_404
from django.utils import timezone


class PayDownPaymentSerializer(serializers.Serializer):
    def validate(self, attrs):
        appointment = self.context["appointment"]

        if appointment.payment.is_paid:
            raise serializers.ValidationError("down payment has already been paid")
        return attrs
     
    def save(self, **kwargs):
        appointment = self.context["appointment"]
        
        service = ZarinPalService()
        result = service.create_payment(
            amount = int(appointment.payment.down_payment),
            description = f"down payment of appointment is {appointment.payment.down_payment}",
            callback_url = settings.CALLBACK_URL,
            mobile = appointment.patient.user.phone)

        appointment.payment.authority = result["authority"]
        appointment.payment.save(update_fields = ["authority"])
        return {
            "payment_url":result["payment_url"],
            "authority":result["authority"],
                }

class DownPaymentResponseSerializer(serializers.Serializer):
    payment_url = serializers.CharField(max_length=100)
    authority = serializers.CharField(max_length=50) 

class VerifyPaymentSerializer(serializers.Serializer):
    authority = serializers.CharField(max_length=100)
    status= serializers.CharField(max_length=15)

    def validate_Status(self, value):
        if value != "OK":
            raise serializers.ValidationError("payment canceled")
        return value
    
    def save(self, **kwargs):
        authority = self.validated_data["authority"]
        status = self.validated_data["status"]
        print(authority)
        print(status)
        service = ZarinPalService()
        payment = get_object_or_404(Payment, authority=authority)
        if payment.is_paid:
            raise serializers.ValidationError("payment has already been paid")

        result = service.verify_payment(
            amount = payment.down_payment,
            authority = payment.authority,
        )
        payment.ref_id = result["ref_id"]
        payment.is_paid = True
        payment.paid_at = timezone.now()
        payment.remaining_amount  = payment.amount_to_pay - payment.down_payment
        payment.card_num = result["card_num"]
        payment.save(update_fields=["ref_id", "is_paid", "remaining_amount", "paid_at","card_num"])
        
        
        return {
            "message":"payment verified successfully",
            "authority":authority,
            "ref_id":payment.ref_id,
            "card_num":result["card_num"]
        } 
class VerifyPaymentResponseSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=50)
    authority = serializers.CharField(max_length=50)
    ref_id = serializers.CharField(max_length=50)
    card_num = serializers.CharField()

class PaymentSerializer(serializers.ModelSerializer):
    name_of_doctor = serializers.CharField(source = "appointment.doctor.user.fullname", read_only=True)
    name_of_patient = serializers.CharField(source = "appointment.patient.user.fullname", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"