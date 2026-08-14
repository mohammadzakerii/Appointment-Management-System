from django.urls import path
from . import views
app_name="appointment"
urlpatterns = [
    path("service/", views.ServiceView.as_view(), name="service"),
    path("service_detail/<int:pk>/", views.ServiceDetailView.as_view(), name="service_detail"),
    path("workinghour/", views.WorkingHourView.as_view(), name="workinghour"),
    path("workinghour_detail/<int:pk>/", views.WorkingHourDetailView.as_view(), name="workinghour_detail"),
    path("workinghour_specefiec_doctor/<int:pk>/", views.WorkinghourOfSpecefiecDoctorView.as_view(), name="specefiec_workinghour"),
    path("doctors/workinghours/list/", views.DoctorWorkingHourDate.as_view(), name="doctors_list_date"),
    path("get_available_slots/<int:service_id>/", views.GetAvailableSlots.as_view(), name="create_slots"),
    path("create_appointment/<int:service_id>/", views.CreateAppointment.as_view(), name="create_appointment"),
    path("list/", views.AppointmentList.as_view(), name="list"),
    path("cancele/<int:appointment_id>/", views.CancelAppointment.as_view(), name="cancele"),
    path("delete/<int:appointment_id>", views.DeleteAppointment.as_view(), name="delete"),
    path("list/specific_patient/<int:patient_id>", views.AppointmentListOfSpecificPatient.as_view(), name="list_specific_patient"),
    path("list/specific_doctor/<int:doctor_id>", views.AppointmentListOfSpecificDoctor.as_view(), name="list_specific_doctor"),
    path("complete_appointment/<int:appointment_id>", views.CompleteAppointment.as_view(), name="complete_appointment")
    
]