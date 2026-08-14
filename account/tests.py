from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from account.models import User,Otp,Doctor,Patient
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token

# Create your tests here.

class RegisterTestcase(APITestCase):

    def setUp(self):
        user = User.objects.create_user(phone="09301234567", identity_code="1230450888", password ="123456", role="patient")

    def test_register_jwt(self):
        data = {
            "identity_code":"1250550333",
            "password":"56720",
            "password2":"56720",
            "role":"patient",
            "phone":"09307795656"
        }
        response = self.client.post(reverse("account:register_jwt"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_jwt_wrong_passwprd(self):
        data = {
                "identity_code":"1250550333",
                "password":"56720",
                "password2":"54985",
                "role":"patient",
                "phone":"09307795656"
                }    

        response = self.client.post(reverse("account:register_jwt"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_jwt_not_numeric_identity_code(self):
        data = {
                "identity_code":"M250550333",
                "password":"56720",
                "password2":"56720",
                "role":"patient",
                "phone":"09307795656"
                }  
        response = self.client.post(reverse("account:register_jwt"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_jwt_not_numeric_phone (self):   
        data = {
                "identity_code":"1250550333",
                "password":"56720",
                "password2":"56720",
                "role":"patient",
                "phone":"0930m795656"
                }  
        response = self.client.post(reverse("account:register_jwt"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_jwt_wrong_len_identity_code(self):
        data = {
                "identity_code":"125055033",
                 "password":"56720",
                "password2":"56720",
                "role":"patient",
                "phone":"09307795656"
                        }  
        response = self.client.post(reverse("account:register_jwt"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  

    def test_register_jwt_wrong_len_phone(self):
        data = {
                "identity_code":"1250550333",
                "password":"56720",
                "password2":"56720",
                "role":"patient",
                "phone":"09307795"
                }  
        response = self.client.post(reverse("account:register_jwt"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)     

    def test_not_unique_identity_code(self):
        data = {
                "identity_code":"12304508888",
                "password":"56720",
                "password2":"56720",
                "role":"patient",
                "phone":"09307795852"
        } 
        response = self.client.post(reverse("account:register_jwt"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#if phone doesnt start with "09"
    def test_wrong_phone_number(self):
        data = {
                "identity_code":"1250550333",
                "password":"56720",
                "password2":"56720",
                "role":"patient",
                "phone":"11307795789"
        }
        response = self.client.post(reverse("account:register_jwt"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 

class LoginTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone="09301234567", identity_code="1230450888", password ="123456", role="patient")

    def test_login_jwt(self):
        data={
            "identity_code":"1230450888",
            "password":"123456"
        }

        response = self.client.post(reverse("account:login_user"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_password(self):
        data={
            "identity_code":"1230450888",
            "password":"123400"
        }
        response = self.client.post(reverse("account:login_user"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_identity_code(self):
        data={
            "identity_code":"1230450000",
            "password":"123456"
        }
        response = self.client.post(reverse("account:login_user"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_user(self):
        
        data={
            "identity_code":"1230450888",
            "password":"123456"
            }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("account:login_user"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class RegisterOrLoginOTPTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(phone="09301234567", identity_code="1230450888", password ="123456", role="patient")

    def test_register_otp(self):
        data={
            "identity_code":"1200361458",
            "phone":"09301234567"
        }
        response = self.client.post(reverse("account:register_login_otp"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_otp(self):
        data={
            "identity_code":"1230450888",
            "phone":"09301234567"
        }
        response = self.client.post(reverse("account:register_login_otp"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_wrong_len_identity_code(self):
        data={
            "identity_code":"120036145846481",
            "phone":"09301234567"
        }
        response = self.client.post(reverse("account:register_login_otp"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)        

    def test_not_numeric_identity_code(self):
        data={
            "identity_code":"m2003614584",
            "phone":"09301234567"
        }
        response = self.client.post(reverse("account:register_login_otp"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_len_identity_code(self): 
        data={
            "identity_code":"1200361",
            "phone":"09301234567"
        }
        response = self.client.post(reverse("account:register_login_otp"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)   

    def test_wrong_len_phone(self):
        data={
            "identity_code":"12003614567",
            "phone":"09301"
        }
        response = self.client.post(reverse("account:register_login_otp"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_None_phone(self):
        data={
            "identity_code":"12003614567"
        }
        response = self.client.post(reverse("account:register_login_otp"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_maximum_failed_count(self):
        user = User.objects.create_user(identity_code="1234564078", phone="09301287896", role="patient", password="123456")
        
        for i in range(6): 
            otp=Otp.objects.create(code=1234, token=f"test token {i}", phone = user.phone, identity_code=user.identity_code, failed=True)
            
        data={
            "identity_code":"1234564078",
            "phone":"09301287896"
        }
        response = self.client.post(reverse("account:register_login_otp"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_minimum_time_for_otp_request_second_time(self):
        user = User.objects.create_user(identity_code="1234564078", phone="09301287896", role="patient", password="123456")
        otp=Otp.objects.create(code=1234, token="test token", phone = user.phone, identity_code=user.identity_code, failed=True)
        otp.created_at = timezone.now()
        otp.save()
        data={
            "identity_code":"1234564078",
            "phone":"09301287896"
        }
        response = self.client.post(reverse("account:register_login_otp"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CheckOtpTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(identity_code="1234564078", phone="09301287896", role="patient", password="123456")
        self.otp =Otp.objects.create(code=1234, token="test token", phone = self.user.phone, identity_code=self.user.identity_code, failed=True)

    def test_right_otp(self):
        data={
            "code":1234
        }
        response = self.client.post(reverse("account:check_otp"), data, headers={"token":self.otp.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_len_code(self):
        data={
            "code":123456
        }
        response = self.client.post(reverse("account:check_otp"), data, headers={"token":self.otp.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_maximum_quentity_wrong_code(self):
        self.otp.attempts = 5
        self.otp.save()
        data={
            "code":1234
        }
        response = self.client.post(reverse("account:check_otp"), data, headers={"token":self.otp.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_maximum_validation_time_otp(self): 
        self.otp.created_at = timezone.now() - timedelta(minutes=3)
        self.otp.save()
        data={
            "code":1234
        }
        response = self.client.post(reverse("account:check_otp"), data, headers={"token":self.otp.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_code(self):
        data={
            "code":1200
        }
        response = self.client.post(reverse("account:check_otp"), data, headers={"token":self.otp.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_token(self):
        data={
            "code":1234
        }
        response = self.client.post(reverse("account:check_otp"), data, headers={"token":"invalid token"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_different_phone(self):
        otp =Otp.objects.create(code=2345, token="test2 token", phone ="09632581447", identity_code=self.user.identity_code, failed=True)
        data={
            "code":1234
        }
        response = self.client.post(reverse("account:check_otp"), data, headers={"token":otp.token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LogoutJwtTokenTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(identity_code="1230123456", phone="09123456789", role="patient", password="123456")
        self.refresh_token = RefreshToken.for_user(self.user)

    def test_logout_jwt_token(self):
        data = {
            "refresh_token":self.refresh_token,
        }
        
        response = self.client.post(reverse("account:logout_jwt"), data, headers={"Authorization":f"Bearer {self.refresh_token.access_token}"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_blacklisted_jwt_token(self):
        self.refresh_token.blacklist()
        data = {
            "refresh_token":self.refresh_token,
        }
                
        response = self.client.post(reverse("account:logout_jwt"), data, headers={"Authorization":f"Bearer {self.refresh_token.access_token}"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_jwt_token(self):
        data = {
        "refresh_token":"invalid token",
        }
                        
        response = self.client.post(reverse("account:logout_jwt"), data, headers={"Authorization":f"Bearer {self.refresh_token.access_token}"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized(self):
        data = {
        "refresh_token":"invalid token",
        }
                                
        response = self.client.post(reverse("account:logout_jwt"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class LogOutAuthTokenTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(identity_code="1230123456", phone="09123456789", role="patient", password="123456")

    def test_logout_authtoken(self):
        token, create = Token.objects.get_or_create(user = self.user)
        response = self.client.post(reverse("account:logout_authtoken"),headers = {"Authorization":f"Token {token.key}"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unathorized(self):
        response = self.client.post(reverse("account:logout_authtoken"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserListTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(identity_code="1230123456", phone="09123456789", role="admin", password="123456")
        self.refresh_token = RefreshToken.for_user(self.user)
        self.user.is_admin = True
        self.user.save()
        
    def test_user_list_success(self):
        response = self.client.get(reverse("account:user_list"), HTTP_AUTHORIZATION = f"Bearer {self.refresh_token.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_admin(self):
        self.user.is_admin = False
        self.user.role = "Doctor"
        self.user.save()
        response = self.client.get(reverse("account:user_list"), HTTP_AUTHORIZATION = f"Bearer {self.refresh_token.access_token}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class UserDetailTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(identity_code="1230123450", phone="09123456780", role="patient", password="123456")
        self.patient =Patient.objects.create(user = self.user)
        self.patient.save()
        self.normal_user = User.objects.create_user(identity_code="1230120000", phone="09123450000", role="patient", password="123456")
        self.patient2 = Patient.objects.create(user = self.normal_user)
        self.patient2.save()

    def test_user_detail_by_doctor_success(self):
        user2 = User.objects.create_user(identity_code="1230123451", phone="09123456781", role="doctor", password="123456")
        doctor = Doctor.objects.create(user = user2)
        doctor.save()
        jwt_token =RefreshToken.for_user(user2)

        
        response = self.client.get(reverse("account:user_detail", kwargs={"pk":self.user.pk}),  HTTP_AUTHORIZATION=f"Bearer {jwt_token.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

    def test_user_detail_by_admin_success(self):
        user3 = User.objects.create_user(identity_code="1230123400", phone="09123456700", role="admin", password="123456")
        user3.admin = True
        user3.save()
        jwt_token =RefreshToken.for_user(user3)
        response = self.client.get(reverse("account:user_detail", kwargs={"pk":self.user.pk}),  HTTP_AUTHORIZATION=f"Bearer {jwt_token.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail_by_userobject_success(self):
        jwt_token =RefreshToken.for_user(self.user)
        response = self.client.get(reverse("account:user_detail", kwargs={"pk":self.user.pk}),  HTTP_AUTHORIZATION=f"Bearer {jwt_token.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  

    def test_user_detail_by_normal_user(self):
        jwt_token = RefreshToken.for_user(self.normal_user)
        response = self.client.get(reverse("account:user_detail", kwargs={"pk":self.user.pk}),  HTTP_AUTHORIZATION=f"Bearer {jwt_token.access_token}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 


class UpdateUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(identity_code="1230123450", phone="09123456780", role="patient", password="123456")
        self.patient =Patient.objects.create(user = self.user)
        self.patient.save()

    def test_update_user_by_user_object_success(self):

        data = {
            "fullname":"mohammadzakeri",
            "phone":"09123456789",
            "password":"567201",
            "password2":"567201"
        }
        self.client.force_authenticate(user = self.user)
        response = self.client.patch(reverse("account:update_user", kwargs={"pk":self.user.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.fullname, "mohammadzakeri")

    def test_update_user_by_admin_success(self):
        admin = User.objects.create_user(identity_code="1230582134", phone="09123456780", role="admin", password="123456")
        admin.is_admin = True
        admin.save()
        data = {
            "fullname":"mohammadzakeri",
            "phone":"09123456789",
        }
        self.client.force_authenticate(user = admin)
        response = self.client.patch(reverse("account:update_user", kwargs={"pk":self.user.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_by_another_user(self):
        normal_user = User.objects.create_user(identity_code="1230121111", phone="09123451111", role="patient", password="123456")
        normal_patient =Patient.objects.create(user = normal_user)
        normal_patient.save()
        data = {
            "fullname":"mohammadzakeri",
            "phone":"09123456789",
        }
        self.client.force_authenticate(user = normal_user)
        response = self.client.patch(reverse("account:update_user", kwargs={"pk":self.user.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class DeleteAccountTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(identity_code="1230123450", phone="09123456780", role="patient", password="123456")
        self.patient =Patient.objects.create(user = self.user)
        self.patient.save()

    def test_delete_account_by_user_object_succes(self):
        self.client.force_authenticate(user = self.user)
        response = self.client.delete(reverse("account:delete", kwargs={"pk":self.user.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_by_another_user(self):
        admin = User.objects.create_user(identity_code="1230123222", phone="09123452222", role="admin", password="123456")
        admin.is_admin = True
        admin.save()
        self.client.force_authenticate(user = admin)
        response = self.client.delete(reverse("account:delete", kwargs={"pk":self.user.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class CompleteProfile(APITestCase):
    def setUp(self):
        self.patient_user = User.objects.create_user(identity_code="1230123450", phone="09123456780", role="patient", password="123456")
        self.patient = Patient.objects.create(user = self.patient_user)
        self.patient.save()

    def test_by_user_onject_success(self):
        data ={
            "father_name":"Ali"
        }
        self.client.force_authenticate(user = self.patient_user)
        response = self.client.patch(reverse("account:complete_profile"), data) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_by_anonymous_user(self):
        data ={
            "father_name":"Ali"
        }
        response = self.client.patch(reverse("account:complete_profile"), data) 
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)    

class DoctorListTestCase(APITestCase):

    def test_doctor_list(self):
        response = self.client.get(reverse("account:doctor_list")) 
        self.assertEqual(response.status_code, status.HTTP_200_OK) 

class PatientListTestCase(APITestCase):

    def test_patient_list_by_admin_success(self):
        admin = User.objects.create_user(identity_code="1230123222", phone="09123452222", role="admin", password="123456")
        admin.is_admin = True
        admin.save()
        self.client.force_authenticate(user = admin)
        response = self.client.get(reverse("account:patient_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_by_normal_user(self):
        user = User.objects.create_user(identity_code="1230123450", phone="09123456780", role="patient", password="123456")
        patient =Patient.objects.create(user = user)
        patient.save()
        self.client.force_authenticate(user = user)
        response = self.client.get(reverse("account:patient_list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_by_doctor_user(self):
        user = User.objects.create_user(identity_code="1230123001", phone="09123456001", role="doctor", password="123456")
        doctor = Doctor.objects.create(user = user)
        doctor.save()        
        self.client.force_authenticate(user = user)
        response = self.client.get(reverse("account:patient_list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_by_anonymous_user(self):
        response = self.client.get(reverse("account:patient_list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
