from django.urls import path
from . import views
app_name = "payment"
urlpatterns = [
    path("pay/down_payment/<int:appointment_id>", views.PayDownPayment.as_view(), name="pay_down_payment"),
    path("verify/", views.VerifyPayment.as_view(), name="verify_payment"),
    path("list/", views.PaymentListView.as_view(), name="payment_list")
]