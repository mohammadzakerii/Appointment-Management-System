from django.urls import path
from . import views
app_name = "payment"
urlpatterns = [
    path("pay/down_payment/<int:appointment_id>", views.PayDownPayment.as_view(), name="pay_down_payment"),
    path("verify/", views.VerifyPayment.as_view(), name="verify_payment"),
    path("list/", views.PaymentListView.as_view(), name="list"),
    path("specific_appointment/<int:appointment_id>", views.Payment_specific_appointment.as_view(), name="specific_appointmnet"),
    path("specific_doctor/<int:doctor_id>", views.payment_specific_doctor.as_view(), name="specific_doctor"),
    path("specific_patient/<int:patient_id>", views.payment_specific_patient.as_view(), name="specific_patient")
]