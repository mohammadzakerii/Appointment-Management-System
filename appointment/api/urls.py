from django.urls import path
from . import views

urlpatterns = [
    path("service/", views.ServiceView.as_view(), name="service"),
    path("service_detail/<int:pk>/", views.ServiceDetailView.as_view(), name="service_detail"),
    path("workinghour/", views.WorkingHourView.as_view(), name="workinghour"),
    path("workinghour_detail/<int:pk>/", views.WorkingHourDetailView.as_view(), name="workinghour_detail"),
    path("workinghour_specefiec_doctor/<int:pk>/", views.WorkinghourOfSpecefiecDoctorView.as_view(), name="specefiec_workinghour"),
    path("doctors/list/", views.DoctorWorkingHourDate.as_view(), name="doctors_list_date"),
    path("get_available_slots/<int:service_id>/", views.GetAvailableSlots.as_view(), name="create_slots"),
    path("create_appointment/<int:service_id>/", views.CreateAppointment.as_view(), name="create_appointment"),
    path("list/", views.AppointmentList.as_view(), name="apppointment"),
    path("cancele/<int:appointment_id>/", views.CancelAppointment.as_view(), name="cancel"),
    path("delete/<int:appointment_id>", views.DeleteAppointment.as_view(), name="delete_appointment"),
    path("list/specefiec_patient/<int:patient_id>", views.AppointmentListOfSpecefiecPatient.as_view(), name="appointment_list_specefiec_patient"),
    path("list/specefiec_doctor/<int:doctor_id>", views.AppointmentListOfSpecefiecDoctor.as_view(), name="appointment_list_specefiec_doctor"),
    path("complete_appointment/<int:appointment_id>", views.CompleteAppointment.as_view(), name="complete_appointment")
    
]