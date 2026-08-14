from django.test import TestCase
from account.models import User, Patient, Doctor
from appointment.models import Appointment, WorkingHour, Payment,Service
from rest_framework.test import APITestCase
from rest_framework import status, serializers
from datetime import timedelta
from django.urls import reverse
from decimal import Decimal
from unittest.mock import Mock, patch
from payment.services import ZarinPalService
import requests
from datetime import datetime

# Create your tests here.
class PaymentTestCase(APITestCase):

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

        self.payment_of_appointment = Payment.objects.create(appointment = self.appointment_obj, amount_to_pay =self.appointment_obj.service.price, down_payment=self.appointment_obj.service.price * Decimal(0.2), remaining_amount=self.appointment_obj.service.price)
        self.payment_of_appointment.save()

    def test_pay_down_payment_by_patient_success(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.post(reverse("payment:pay_down_payment", kwargs={"appointment_id":self.appointment_obj.id}))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ZarinpalServiceTestCase(TestCase):
    @patch("payment.services.requests.post")
    def test_create_payment_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data":{
                "code":100,
                "authority": "TEST_AUTHORITY"
            }     
        }  
        mock_post.return_value = mock_response
        service = ZarinPalService()
        result = service.create_payment(
            amount = 300000,
            description = "test description",
            callback_url="http://test.com/callback"
        )

        self.assertEqual(result["authority"], "TEST_AUTHORITY")
        self.assertEqual(result["payment_url"], "https://sandbox.zarinpal.com/pg/StartPay/TEST_AUTHORITY") 
         

        mock_post.assert_called_once_with(
            service.REQUEST_URL,
            json={
                "merchant_id":service.merchant_id,
                "amount":300000,
                "callback_url":"http://test.com/callback",
                "description":"test description"
            },
            timeout=10) 
            
        
    @patch("payment.services.requests.post")
    def test_create_payment_failed(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data":{
                "code": -9,
                "authority":""
            },
            "errors":"Invalid merchant"
        }
        mock_post.return_value = mock_response
        service = ZarinPalService()
        with self.assertRaises(Exception):
            service.create_payment(
               amount = 300000,
               description = "test description",
               callback_url="http://test.com/callback"  
            )
        mock_post.assert_called_once_with(
            service.REQUEST_URL,
            json={
            "merchant_id":service.merchant_id,
            "amount":300000,
            "callback_url":"http://test.com/callback",
            "description":"test description"
            },
            timeout=10) 


    @patch("payment.services.requests.post")
    def test_create_payment_with_mobile_and_email(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data":{
                "code": 100,
                "authority":"TEST_AUTHORITY"
            }
        }
        mock_post.return_value = mock_response
        service = ZarinPalService()
        result = service.create_payment(
            amount=300000,
            description = "test description",
            callback_url="http://test.com/callback",
            mobile = "09121234567",
            email = "test@gmail.com"
        )
        mock_post.assert_called_once_with(
            service.REQUEST_URL,
            json = {
                "merchant_id":service.merchant_id,
                "amount":300000,
                "description":"test description",
                "callback_url":"http://test.com/callback",
                "metadata":{
                    "mobile":"09121234567",
                    "email": "test@gmail.com"
                } 
            },
            timeout=10
        )

    @patch("payment.services.requests.post")
    def test_create_payment_with_mobile_no_email(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data":{
                "code": 100,
                "authority": "TEST_AUTHORITY"
            }
        }
        mock_post.return_value = mock_response
        service = ZarinPalService()
        result = service.create_payment(
            amount=300000,
            description = "test description",
            callback_url="http://test.com/callback",
            mobile = "09121234567"
        )
        mock_post.assert_called_once_with(
            service.REQUEST_URL,
            json={
                "merchant_id":service.merchant_id,
                "amount":300000,
                "callback_url":"http://test.com/callback",
                "description":"test description",
                "metadata":{
                "mobile":"09121234567" 
                }
            },
            timeout=10
        )

    @patch("payment.services.requests.post")
    def test_create_payment_with_email_no_mobile(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
        "data":{
            "code": 100,
            "authority": "TEST_AUTHORITY"
         }
            }
        mock_post.return_value = mock_response
        service = ZarinPalService()
        result = service.create_payment(
            amount=300000,
            description = "test description",
            callback_url="http://test.com/callback",
            email = "test@gmail.com"
        )
        mock_post.assert_called_once_with(
        service.REQUEST_URL,
            json={
                "merchant_id":service.merchant_id,
                "amount":300000,
                "callback_url":"http://test.com/callback",
                "description":"test description",
                "metadata":{
                "email":"test@gmail.com" 
                    }
                },
                    timeout=10
                )
    @patch("payment.services.requests.post")
    def test_create_payment_http_error(self, mock_post):
        mock_response = Mock()
        mock_response.stauts = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "500 Server Error"
        )
        mock_post.return_value = mock_response

        service = ZarinPalService()

        with self.assertRaises(requests.HTTPError):
            service.create_payment(
            amount=300000,
            description = "test description",
            callback_url="http://test.com/callback",
            )
        mock_post.assert_called_once_with(
            service.REQUEST_URL,
            json={
                "merchant_id":service.merchant_id,
                "amount":300000,
                "callback_url":"http://test.com/callback",
                "description":"test description",
                },
                timeout=10
                )

    @patch("payment.services.requests.post")
    def test_verify_payment_success_100(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value ={
            "data":{
                "code":100,
                "ref_id":123456,
                "card_pan":"5859****8641",
                "message":"payment verified successfully"
            }
        }
        mock_post.return_value = mock_response
        service = ZarinPalService()
        result = service.verify_payment(
            authority ="TEST_AUTHORITY",
            amount= 300000    
        )

        self.assertEqual(result["code"],100),
        self.assertEqual(result["ref_id"],123456 )
        self.assertEqual(result["card_num"],"5859****8641")
        self.assertEqual(result["message"], "payment verified successfully")
        
        mock_post.assert_called_once_with(
            service.VERIFY_URL,
            json={
                "merchant_id":service.merchant_id,
                "authority": "TEST_AUTHORITY",
                "amount":300000
            },
            timeout=10
        ) 

    @patch("payment.services.requests.post")
    def test_verify_payment_success_101(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value ={
            "data":{
                "code":101,
                "ref_id":123456,
                "card_pan":"5859****8641",
                "message":"payment verified successfully"
            }
        }
        mock_post.return_value = mock_response
        service = ZarinPalService()
        result = service.verify_payment(
            authority ="TEST_AUTHORITY",
            amount= 300000    
        )

        self.assertEqual(result["code"],101)
        self.assertEqual(result["ref_id"],123456 )
        self.assertEqual(result["card_num"],"5859****8641")
        self.assertEqual(result["message"], "payment verified successfully")
        
        mock_post.assert_called_once_with(
            service.VERIFY_URL,
            json={
                "merchant_id":service.merchant_id,
                "authority": "TEST_AUTHORITY",
                "amount":300000
            },
            timeout=10
        )  


    @patch("payment.services.requests.post")
    def test_verify_payment_failed(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data":{
                "code":-9,
                 
            },
            "errors":"verify payment failed"
        }
        mock_post.return_value = mock_response
        service = ZarinPalService()
        with self.assertRaises(serializers.ValidationError):
            service.verify_payment(
                amount=300000,
                authority="TEST_AUTHORITY"
            )
        mock_post.assert_called_once_with(
            service.VERIFY_URL,
            json={
                "merchant_id":service.merchant_id,
                "authority":"TEST_AUTHORITY",
                "amount":300000
            },
            timeout=10
        )

    @patch("payment.services.requests.post")
    def test_verify_payment_http_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect= requests.HTTPError(
            "500 HTTP Error"
        )
        mock_post.return_value = mock_response
        service = ZarinPalService()
        with self.assertRaises(requests.HTTPError):
             service.verify_payment(
                amount=300000,
                authority="TEST_AUTHORITY"
            )
        mock_response.raise_for_status.assert_called_once()     
        mock_post.assert_called_once_with(
            service.VERIFY_URL,
            json={
                "merchant_id":service.merchant_id,
                "authority":"TEST_AUTHORITY",
                "amount":300000
            },
            timeout=10
        )


class PaymentListTestCase(APITestCase):
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
        self.payment_obj = Payment.objects.create(appointment=self.appointment_obj, amount_to_pay=300000, down_payment=300000 * Decimal(0.2), remaining_amount = 0, is_paid=True, ref_id=1234, card_num="585******645")
        self.payment_obj.save()

    def test_payment_list_by_admin_success(self):
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.get(reverse("payment:list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_list_by_patient(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("payment:list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_payment_list_by_owner_doctor(self):
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.get(reverse("payment:list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_payment_list_filter_is_paid_True(self):
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.get(reverse("payment:list"),{"is_paid":True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_list_specific_doctor_success(self):
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.get(reverse("payment:specific_doctor", kwargs={"doctor_id":self.payment_obj.appointment.doctor.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_list_specific_doctor_by_admin_success(self):
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.get(reverse("payment:specific_doctor", kwargs={"doctor_id":self.payment_obj.appointment.doctor.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_list_specific_doctor_by_patient(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("payment:specific_doctor", kwargs={"doctor_id":self.payment_obj.appointment.doctor.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_payment_list_specific_doctor_unauthorized(self):
        response = self.client.get(reverse("payment:specific_doctor", kwargs={"doctor_id":self.payment_obj.appointment.doctor.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_list_specific_doctor_by_another_doctor(self):
        self.client.force_authenticate(user = self.doctor_user2)
        response = self.client.get(reverse("payment:specific_doctor", kwargs={"doctor_id":self.payment_obj.appointment.doctor.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_payment_list_specific_doctor_year_filter_success (self):
        Payment.objects.filter(pk=self.payment_obj.pk).update(created_at=datetime(2026,5,10,12,0,0))
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.get(reverse("payment:specific_doctor", kwargs={"doctor_id":self.doctor_obj.pk}), {"created_at__year":2026})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(len(response.data["results"]), 1)    

        
    def test_payment_list_specific_doctor_wrong_year_filter(self):
        Payment.objects.filter(pk=self.payment_obj.pk).update(created_at=datetime(2026,5,10,12,0,0))
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.get(reverse("payment:specific_doctor", kwargs={"doctor_id":self.doctor_obj.pk}), {"created_at__year":2027})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(len(response.data["results"]), 0)

    def test_payment_list_specific_doctor_fullname_of_doctor_or_patient_filter_success(self):
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.get(reverse("payment:specific_doctor", kwargs={"doctor_id":self.doctor_obj.pk}), {"search":"Aliahmadi"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_payment_list_dpecific_patient_by_owner_patient_success(self):
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("payment:specific_patient", kwargs={"patient_id":self.patient_obj.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_list_specific_patient_by_admin_success(self):
        self.client.force_authenticate(user = self.admin_user)
        response = self.client.get(reverse("payment:specific_patient", kwargs={"patient_id":self.patient_obj.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_list_specific_patient_by_doctor(self):
        self.client.force_authenticate(user = self.doctor_user)
        response = self.client.get(reverse("payment:specific_patient", kwargs={"patient_id":self.patient_obj.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_payment_list_specific_patient_by_another_patient(self):
        self.client.force_authenticate(user = self.patient_user2)
        response = self.client.get(reverse("payment:specific_patient", kwargs={"patient_id":self.patient_obj.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_payment_list_specific_patinet_unauthorized(self):
        response = self.client.get(reverse("payment:specific_patient", kwargs={"patient_id":self.patient_obj.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_list_specific_patient_year_filter_success(self):
        Payment.objects.filter(pk=self.payment_obj.pk).update(created_at = datetime(2026,10,3,10,30,0))
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("payment:specific_patient", kwargs={"patient_id":self.patient_obj.pk}),{"created_at__year":2026})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1) 

    def test_payment_list_specific_patient_yaer_filter_not_found(self):
        Payment.objects.filter(pk=self.payment_obj.pk).update(created_at = datetime(2026,10,3,10,30,0))
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("payment:specific_patient", kwargs={"patient_id":self.patient_obj.pk}),{"created_at__year":2027})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_payment_list_specific_patient__name_of_doctor_filter_success(self):
        Payment.objects.filter(pk=self.payment_obj.pk)
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("payment:specific_patient", kwargs={"patient_id":self.patient_obj.pk}),{"search":"RezaMohammadi"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_payment_list_specific_name_of_doctor_not_found(self):
        Payment.objects.filter(pk=self.payment_obj.pk)
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.get(reverse("payment:specific_patient", kwargs={"patient_id":self.patient_obj.pk}),{"search":"HamedMaleki"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
        




        




        
        








   


        
        
