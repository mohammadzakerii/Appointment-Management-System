from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from account.models import User,Otp,Doctor,Patient
from appointment.models import Service, Appointment, WorkingHour, Payment
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from decimal import Decimal

# Create your tests here.

class CreateServiceTestCase(APITestCase):
    def setUp(self):
        self.doctor_user = User.objects.create_user(identity_code="1230123457", phone="09121234567", role="doctor", password="12345")
        self.doctor_obj = Doctor.objects.create(user = self.doctor_user)
        self.doctor_obj.save()
        self.admin_user = User.objects.create_user(identity_code="1230123222", phone="09121232222", role="admin", password="12345")
        self.admin_user.is_admin = True
        self.admin_user.save()

    def test_create_service_success(self):
        data = {
            "name":"dentistery service",
            "price":300000,
            "slot_duration":30,
             
        }
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.post(reverse("appointment:service"), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unathorized(self):
        data = {
            "name":"dentistery service",
            "price":300000,
            "slot_duration":30, 
        }
        response = self.client.post(reverse("appointment:service"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_by_admin(self):
        data = {
        "name":"dentistery service",
        "price":300000,
        "slot_duration":30,
        "doctor":self.doctor_obj.id
        }
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.post(reverse("appointment:service"), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#doctor cant set doctor field so not owner doctor cant create a service for another doctor 
    def test_by_another_doctor(self):
        not_owner_doctor_user = User.objects.create_user(identity_code="1230123888", phone="09121237777", role="doctor", password="12345")
        not_owner_doctor_object = Doctor.objects.create(user = not_owner_doctor_user)
        not_owner_doctor_object.save()

        data = {
        "name":"dentistery service",
        "price":300000,
        "slot_duration":30,
        "doctor":self.doctor_obj.id
        }
        self.client.force_authenticate(user = not_owner_doctor_user)
        response = self.client.post(reverse("appointment:service"), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_by_patient(self):
        patient_user = User.objects.create_user(identity_code="1230123777", phone="09121237777", role="patient", password="12345")
        patient_obj = Patient.objects.create(user = patient_user)
        patient_obj.save()
        data = {
        "name":"dentistery service",
        "price":300000,
        "slot_duration":30,
        "doctor":self.doctor_obj.id
        }
        self.client.force_authenticate(user = patient_user)
        response = self.client.post(reverse("appointment:service"), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ServiceListTestCase(APITestCase):

    def setUp(self):
        self.patient_user = User.objects.create_user(identity_code="1230123777", phone="09121237777", role="patient", password="12345")
        self.patient_obj = Patient.objects.create(user = self.patient_user)
        self.patient_obj.save()

    def test_service_list_success(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("appointment:service"))
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_service_list_unathorized(self):
        response = self.client.get(reverse("appointment:service"))
        self.assertEqual(response.status_code,status.HTTP_200_OK)

class ServiceDetailTestCase(APITestCase):
    def setUp(self):
        self.doctor_user = User.objects.create_user(identity_code="1230123777", phone="09121237777", role="doctor", password="12345")
        self.doctor_obj = Doctor.objects.create(user = self.doctor_user)
        self.doctor_obj.save()
        self.doctor_service = Service.objects.create(doctor=self.doctor_obj, name="dentistery service", price = 300000, slot_duration = timedelta(minutes=30))

    def test_get_service_detail_success(self):
        response = self.client.get(reverse("appointment:service_detail", kwargs={"pk":self.doctor_service.pk}))
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_update_service_by_owner_doctor_success(self):
        data ={
            "name":"updated dentistery service"
        }
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.patch(reverse("appointment:service_detail", kwargs={"pk":self.doctor_service.pk} ), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_service_by_admin(self):
        admin_user = User.objects.create_user(identity_code="123012333", phone="09121233333", role="admin", password="12345")
        admin_user.is_admin = True
        admin_user.save()

        data ={
            "name":"updated dentistery service"
        }
        
        self.client.force_authenticate(user = admin_user)
        response = self.client.patch(reverse("appointment:service_detail", kwargs={"pk":self.doctor_service.pk} ), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_service_by_patient(self):
        patient_user = User.objects.create_user(identity_code="1230123111", phone="09121231111", role="patient", password="12345")
        patient_obj = Patient.objects.create(user = patient_user)
        patient_obj.save()

        data ={
            "name":"updated dentistery service"
        }
        self.client.force_authenticate(user = patient_user)
        response = self.client.patch(reverse("appointment:service_detail", kwargs={"pk":self.doctor_service.pk} ), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_service_by_another_doctor(self):
        doctor_user2 = User.objects.create_user(identity_code="1230123999", phone="09121239999", role="doctor", password="12345")
        doctor_obj2 = Doctor.objects.create(user = doctor_user2)
        doctor_obj2.save()
        data ={
            "name":"updated dentistery service",
            
        }
        self.client.force_authenticate(user = doctor_user2)
        response = self.client.patch(reverse("appointment:service_detail", kwargs={"pk":self.doctor_service.pk} ), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_service_unauthorized(self):
        data ={
            "name":"updated dentistery service",    
        }
        
        response = self.client.patch(reverse("appointment:service_detail", kwargs={"pk":self.doctor_service.pk} ), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_service_by_another_doctor(self):
        doctor_user2 = User.objects.create_user(identity_code="1230123999", phone="09121239999", role="doctor", password="12345")
        doctor_obj2 = Doctor.objects.create(user = doctor_user2)
        doctor_obj2.save()
                
        self.client.force_authenticate(user = doctor_user2)
        response = self.client.delete(reverse("appointment:service_detail", kwargs={"pk":self.doctor_service.pk} ))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_service_by_patient(self):
        patient_user = User.objects.create_user(identity_code="1230123111", phone="09121231111", role="patient", password="12345")
        patient_obj = Patient.objects.create(user = patient_user)
        patient_obj.save()
        
        self.client.force_authenticate(user = patient_user)
        response = self.client.delete(reverse("appointment:service_detail", kwargs={"pk":self.doctor_service.pk} ))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_service_by_admin_success(self): 
        admin_user = User.objects.create_user(identity_code="1230123333", phone="09121233333", role="admin", password="12345")
        admin_user.is_admin = True
        admin_user.save()
                
        self.client.force_authenticate(user = admin_user)
        response = self.client.delete(reverse("appointment:service_detail", kwargs={"pk":self.doctor_service.pk} ))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)  

    def test_delete_service_by_owner_doctor_success(self):
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.delete(reverse("appointment:service_detail", kwargs={"pk":self.doctor_service.pk} ))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ListCreatWorkingHour(APITestCase):

    def setUp(self):
        self.doctor_user = User.objects.create_user(identity_code="1230123777", phone="09121237777", role="doctor", password="12345", fullname="AliAhmadi")
        self.doctor_obj = Doctor.objects.create(user = self.doctor_user)
        self.doctor_obj.save()

        self.workinghour = WorkingHour.objects.create(doctor = self.doctor_obj, start_work_time="10:00:00", end_work_time="12:00:00", days_of_week=1)
        self.workinghour.save()

        self.patient_user = User.objects.create_user(identity_code="1230123111", phone="09121231111", role="patient", password="12345")
        self.patient_obj = Patient.objects.create(user = self.patient_user)
        self.patient_obj.save()

        self.admin_user = User.objects.create_user(identity_code="123012333", phone="09121233333", role="admin", password="12345", is_admin=True)

        self.doctor_user2 = User.objects.create_user(identity_code="1230123888", phone="09121238888", role="doctor", password="12345", fullname="RezaMoradi")
        self.doctor_obj2 = Doctor.objects.create(user = self.doctor_user2)
        self.doctor_obj2.save()

#safe method is allowed
    def test_workinghour_list_success(self):
        response = self.client.get(reverse("appointment:workinghour"))
        print(response.status_code)
        print(response.data)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_create_workinghour_owner_doctor_set_doctor_field(self):
        data={
            "start_work_time":"09:00:00",
            "end_work_time":"13:00:00",
            "days_of_week":1,
            "doctor":self.doctor_obj.pk
        }
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.post(reverse("appointment:workinghour"), data)
        print(response.status_code)
        print(response.data)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_workinghour_doctor_success(self):
        data={
        "start_work_time":"09:00:00",
        "end_work_time":"13:00:00",
        "days_of_week":2,
        
        
        }
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.post(reverse("appointment:workinghour"), data)
        print(response.data)
        print(response.status_code)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)        

    def test_create_repeated_workinghor_same_day_same_doctor(self):
            data={
            "start_work_time":"09:00:00",
            "end_work_time":"13:00:00",
            "days_of_week":1,
            }
            self.client.force_authenticate(user = self.doctor_user)
            response = self.client.post(reverse("appointment:workinghour"), data)
            print(response.data)
            print(response.status_code)
            self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST) 

    def test_create_workinghor_by_admin(self):
        data={
        "start_work_time":"09:00:00",
        "end_work_time":"13:00:00",
        "days_of_week":2,
        "doctor":self.doctor_obj.pk
        }
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.post(reverse("appointment:workinghour"), data)
        print(response.data)
        print(response.status_code)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    def test_create_workinghor_by_admin_without_doctor_field(self):
        data={
        "start_work_time":"09:00:00",
        "end_work_time":"13:00:00",
        "days_of_week":2,
        
        }
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.post(reverse("appointment:workinghour"), data)
        print(response.data)
        print(response.status_code)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_workinghour_by_patient(self):
        data={
            "start_work_time":"09:00:00",
            "end_work_time":"13:00:00",
            "days_of_week":2,
            "doctor":self.doctor_obj.pk     
            }
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.post(reverse("appointment:workinghour"), data)
        print(response.data)
        print(response.status_code)
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

    def test_create_workinghour_by_anonymous(self):
        data={
        "start_work_time":"09:00:00",
        "end_work_time":"13:00:00",
        "days_of_week":2,
        "doctor":self.doctor_obj.pk     
        }
        
        response = self.client.post(reverse("appointment:workinghour"), data)
        print(response.data)
        print(response.status_code)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_create_workinghour_by_another_doctor(self):
        data={
        "start_work_time":"09:00:00",
        "end_work_time":"13:00:00",
        "days_of_week":2,
        "doctor":self.doctor_obj.pk     
        }
        self.client.force_authenticate(user = self.doctor_user2)  
        response = self.client.post(reverse("appointment:workinghour"), data)
        print(response.data)
        print(response.status_code)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)   

class WorkingHourDetailTestCase(APITestCase):

    def setUp(self):
        self.patient_user = User.objects.create_user(identity_code="1230123777", phone="09121237777", role="patient", password="12345", fullname="AliAhmadi")
        self.patient_obj = Doctor.objects.create(user = self.patient_user)
        self.patient_obj.save()

        self.doctor_user = User.objects.create_user(identity_code="1230123888", phone="09121238888", role="doctor", password="12345", fullname="AhmadRazai")
        self.doctor_obj = Doctor.objects.create(user = self.doctor_user)
        self.doctor_obj.save()

        self.doctor_user2 = User.objects.create_user(identity_code="1230123555", phone="09121235555", role="doctor", password="12345", fullname="RezaMohammadi")
        self.doctor_obj2 = Doctor.objects.create(user = self.doctor_user2)
        self.doctor_obj2.save()
        

        self.doctor_workinghour = WorkingHour.objects.create(start_work_time="09:00:00", end_work_time="12:00:00", doctor=self.doctor_obj, days_of_week=1)
        self.doctor_workinghour2 = WorkingHour.objects.create(start_work_time="09:00:00", end_work_time="12:00:00", doctor=self.doctor_obj, days_of_week=2)

        self.admin_user = User.objects.create_user(identity_code="1230123666", phone="09121236666", role="admin", password="12345", fullname="AliAhmadi", is_admin=True)

    def test_workinghour_detail_success(self):
        self.client.force_authenticate(user =self.patient_user)
        response = self.client.get(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
 

    def test_update_workinghour_by_owner_success(self):
        data={
            "start_work_time":"08:00:00"
        }
        self.client.force_authenticate(user =self.doctor_user)
        response = self.client.patch(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}),data)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

    def test_updated_workinghor_by_patient(self):
        data={
        "start_work_time":"08:00:00"
        }
        self.client.force_authenticate(user =self.patient_user)
        response = self.client.patch(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}),data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_workinhour_by_admin_success(self):
        data={
        "start_work_time":"08:00:00"
        }
        self.client.force_authenticate(user =self.admin_user)
        response = self.client.patch(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}),data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_workinghour_another_doctor(self):
        data={
        "start_work_time":"08:00:00"
        }
        self.client.force_authenticate(user =self.doctor_user2)
        response = self.client.patch(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_update_workinghour_repeated_day(self):
        data={
        "days_of_week":2
        }
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.patch(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}),data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_delete_workinghour_success(self):
        self.client.force_authenticate(user =self.doctor_user)
        response = self.client.delete(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_workinhour_by_patient(self):
        self.client.force_authenticate(user =self.patient_user)
        response = self.client.delete(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_workinghour_by_another_doctor(self):
        self.client.force_authenticate(user =self.doctor_user2)
        response = self.client.delete(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_delete_workinghour_by_admin_success(self):
        self.client.force_authenticate(user =self.admin_user)
        response = self.client.delete(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class WorkingHourSpecefiecDoctorTestCase(APITestCase):

    def setUp(self):
        self.doctor_user = User.objects.create_user(identity_code="1230123888", phone="09121238888", role="doctor", password="12345", fullname="AliAhmadi")
        self.doctor_obj = Doctor.objects.create(user = self.doctor_user)
        self.doctor_obj.save()
        self.doctor_workinghour = WorkingHour.objects.create(start_work_time="09:00:00", end_work_time="12:00:00", doctor=self.doctor_obj, days_of_week=1)

    def test_success(self):
        response = self.client.get(reverse("appointment:workinghour_detail", kwargs={"pk":self.doctor_workinghour.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class WorkinghourDateTestCase(APITestCase):

    def setUp(self):
        self.doctor_user = User.objects.create_user(identity_code="1230123888", phone="09121238888", role="doctor", password="12345", fullname="AliAhmadi")
        self.doctor_obj = Doctor.objects.create(user = self.doctor_user)
        self.doctor_obj.save()
        self.doctor_workinghour = WorkingHour.objects.create(start_work_time="09:00:00", end_work_time="12:00:00", doctor=self.doctor_obj, days_of_week=1)
        

    def test_workinghourdate_success(self):
        response = self.client.get(reverse("appointment:doctors_list_date"),{"date":"2026-10-13"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAvailableSlotsTestCase(APITestCase):
    def setUp(self):
        self.patient_user = User.objects.create_user(identity_code="1230123777", phone="09121237777", role="patient", password="12345", fullname="AliAhmadi")
        self.patient_obj = Doctor.objects.create(user = self.patient_user)
        self.patient_obj.save()

        self.doctor_user = User.objects.create_user(identity_code="1230123888", phone="09121238888", role="doctor", password="12345", fullname="AhmadRezai")
        self.doctor_obj = Doctor.objects.create(user = self.doctor_user)
        self.doctor_obj.save()

        self.doctor_workinghour = WorkingHour.objects.create(start_work_time="09:00:00", end_work_time="12:00:00", doctor=self.doctor_obj, days_of_week=1)
        self.doctor_workinghour.save()
        self.doctor_service = Service.objects.create(name="dentistry service", slot_duration=timedelta(minutes=30), price=300000, doctor=self.doctor_obj)
        self.doctor_service.save()

    def test_getavailableslots_duccess(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("appointment:create_slots", kwargs={"service_id":self.doctor_service.pk}),{"date":"2026-10-13"}) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AppointmentTestCase(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(identity_code="1230123666", phone="09121236666", role="admin", password="12345", fullname="ArmanTavakoli", is_admin=True)

        self.patient_user = User.objects.create_user(identity_code="1230123777", phone="09121237777", role="patient", password="12345", fullname="AliAhmadi")
        self.patient_obj = Patient.objects.create(user = self.patient_user)
        self.patient_obj.save()

        self.patient_user2 = User.objects.create_user(identity_code="1230123444", phone="09121234444", role="patient", password="12345", fullname="AhmadRezai")
        self.patient_obj2 = Patient.objects.create(user = self.patient_user2)
        self.patient_obj.save()

        self.doctor_user = User.objects.create_user(identity_code="1230123888", phone="09121238888", role="doctor", password="12345", fullname="RezaMohammadi")
        self.doctor_obj = Doctor.objects.create(user = self.doctor_user)
        self.doctor_obj.save()

        self.doctor_user2 = User.objects.create_user(identity_code="1230123555", phone="09121235555", role="doctor", password="12345", fullname="VahidKarimi")
        self.doctor_obj2 = Doctor.objects.create(user = self.doctor_user2)
        self.doctor_obj2.save()

        self.doctor_service = Service.objects.create(name="dentistry service", slot_duration=timedelta(minutes=30), price=300000, doctor=self.doctor_obj)
        self.doctor_service.save()

        self.doctor_workinghour = WorkingHour.objects.create(start_work_time="09:00:00", end_work_time="12:00:00", doctor=self.doctor_obj, days_of_week=1)
        self.doctor_workinghour.save()

        self.appointment_obj = Appointment.objects.create(doctor = self.doctor_obj, date="2026-10-13", patient=self.patient_obj, start_time="09:30:00"  , service=self.doctor_service, status="scheduled")
        self.appointment_obj.save()

        self.payment_obj = Payment.objects.create(appointment=self.appointment_obj, amount_to_pay=300000, down_payment=300000 * Decimal(0.2), remaining_amount = 240000, is_paid=True, ref_id=1234)
        self.payment_obj.save()

    def test_create_appointment_succes(self):
        data = {
            "date":"2026-10-13",
            "start_time":"09:00:00"
        }
        self.client.force_authenticate(user = self.patient_user2)
        response = self.client.post(reverse("appointment:create_appointment", kwargs={"service_id":self.doctor_service.pk}),data) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_appointment_in_booked_time(self):
        data = {
        "date":"2026-10-13",
        "start_time":"09:30:00"
        }
        self.client.force_authenticate(user = self.patient_user2)
        response = self.client.post(reverse("appointment:create_appointment", kwargs={"service_id":self.doctor_service.pk}),data) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  

    def test_create_appointment_same_date_same_patient(self):
        data = {
        "date":"2026-10-13",
        "start_time":"10:00:00"
        }
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.post(reverse("appointment:create_appointment", kwargs={"service_id":self.doctor_service.pk}),data) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 

    def test_create_appointment_not_working_day_of_doctor(self):
        data = {
        "date":"2026-10-14",
        "start_time":"09:30:00"
        }
        self.client.force_authenticate(user = self.patient_user2)
        response = self.client.post(reverse("appointment:create_appointment", kwargs={"service_id":self.doctor_service.pk}),data) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_not_in_time_slots(self):
        data = {
        "date":"2026-10-13",
        "start_time":"09:45:00"
        }
        self.client.force_authenticate(user = self.patient_user2)
        response = self.client.post(reverse("appointment:create_appointment", kwargs={"service_id":self.doctor_service.pk}),data) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_past_date(self):
        data = {
        "date":"2020-01-13",
        "start_time":"09:30:00"
        }
        self.client.force_authenticate(user = self.patient_user2)
        response = self.client.post(reverse("appointment:create_appointment", kwargs={"service_id":self.doctor_service.pk}),data) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointmnet_unauthorized(self):
        data = {
        "date":"2026-10-13",
        "start_time":"09:30:00"
        }
        response = self.client.post(reverse("appointment:create_appointment", kwargs={"service_id":self.doctor_service.pk}),data) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_appointment_list_by_doctor(self):
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.get(reverse("appointment:list")) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_appointment_list_by_admin(self):
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.get(reverse("appointment:list")) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

    def test_appointment_list_by_patient(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("appointment:list")) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_appointment_list_unathorized(self):
        response = self.client.get(reverse("appointment:list")) 
        print(response.data)  
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cancele_appointment_by_patient_success(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.patch(reverse("appointment:cancele", kwargs={"appointment_id":self.appointment_obj.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancele_appointment_by_admin_success(self):
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.patch(reverse("appointment:cancele", kwargs={"appointment_id":self.appointment_obj.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cencele_appointment_by_doctor(self):
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.patch(reverse("appointment:cancele", kwargs={"appointment_id":self.appointment_obj.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cencele_completed_appointment(self):
        completed_appointment = Appointment.objects.create(doctor = self.doctor_obj, date="2026-10-21", patient=self.patient_obj, start_time="09:30:00"  , service=self.doctor_service, status="completed")
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.patch(reverse("appointment:cancele", kwargs={"appointment_id":completed_appointment.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_cenceled_appointment(self):
        canceled_appointment = Appointment.objects.create(doctor = self.doctor_obj, date="2026-10-21", patient=self.patient_obj, start_time="09:30:00"  , service=self.doctor_service, status="canceled")
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.patch(reverse("appointment:cancele", kwargs={"appointment_id":canceled_appointment.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  

    def test_delete_appointment_by_patient(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.delete(reverse("appointment:delete", kwargs={"appointment_id":self.appointment_obj.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_appointmnet_by_doctor(self):
        self.client.force_authenticate(user = self.appointment_obj.doctor.user)
        response = self.client.delete(reverse("appointment:delete", kwargs={"appointment_id":self.appointment_obj.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_appointment_by_another_doctor(self):
        self.client.force_authenticate(user = self.doctor_user2)
        response = self.client.delete(reverse("appointment:delete", kwargs={"appointment_id":self.appointment_obj.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_appointment_by_addmin_success(self):
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.delete(reverse("appointment:delete", kwargs={"appointment_id":self.appointment_obj.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_appointment_list_specific_patient_by_owner_succcess(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("appointment:list_specific_patient", kwargs={"patient_id":self.patient_user.patient.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_appointment_list_specific_patient_by_admin_success(self):
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.get(reverse("appointment:list_specific_patient", kwargs={"patient_id":self.patient_user.patient.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_appointment_list_specific_patient_by_doctor_success(self):
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.get(reverse("appointment:list_specific_patient", kwargs={"patient_id":self.patient_user.patient.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_appointment_list_specific_patient_by_anonymous(self):
        response = self.client.get(reverse("appointment:list_specific_patient", kwargs={"patient_id":self.patient_user.patient.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_appointment_list_specific_patient_by_another_patient(self):
        self.client.force_authenticate(user = self.patient_user2)
        response = self.client.get(reverse("appointment:list_specific_patient", kwargs={"patient_id":self.patient_user.patient.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_appointment_list_specific_doctor_by_owner_doctor_success(self):
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.get(reverse("appointment:list_specific_doctor", kwargs={"doctor_id":self.doctor_user.doctor.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_appointmnet_list_specific_doctor_by_admin_success(self):
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.get(reverse("appointment:list_specific_doctor", kwargs={"doctor_id":self.doctor_user.doctor.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_appointment_list_specific_doctor_by_another_doctor(self):
        self.client.force_authenticate(user = self.doctor_user2)
        response = self.client.get(reverse("appointment:list_specific_doctor", kwargs={"doctor_id":self.doctor_user.doctor.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_appointment_list_specific_doctor_by_patient(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("appointment:list_specific_doctor", kwargs={"doctor_id":self.doctor_user.doctor.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_appointment_list_specific_doctor_unauthorized(self):
        response = self.client.get(reverse("appointment:list_specific_doctor", kwargs={"doctor_id":self.doctor_user.doctor.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_complete_appointment_by_admin_success(self):
        data={
            "final_payment":240000,
            "ref_id":2345,
            "card_num":7896
        }
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.post(reverse("appointment:complete_appointment",kwargs={"appointment_id":self.appointment_obj.pk}), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_complete_appointment_by_owner_doctor_success(self):
        data={
            "final_payment":240000,
            "ref_id":2345,
            "card_num":7896
        }
        self.client.force_authenticate(user = self.appointment_obj.doctor.user)
        response = self.client.post(reverse("appointment:complete_appointment",kwargs={"appointment_id":self.appointment_obj.pk}), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_complete_appointment_by_patient(self):
        data={
            "final_payment":240000,
            "ref_id":2345,
            "card_num":7896
        }
        self.client.force_authenticate(user = self.appointment_obj.patient.user)
        response = self.client.post(reverse("appointment:complete_appointment",kwargs={"appointment_id":self.appointment_obj.pk}), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_complete_appointment_unauthorized(self):       
        data={
            "final_payment":240000,
            "ref_id":2345,
            "card_num":7896
        }
        response = self.client.post(reverse("appointment:complete_appointment",kwargs={"appointment_id":self.appointment_obj.pk}), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)















    






                        









                  

       






    
             




















