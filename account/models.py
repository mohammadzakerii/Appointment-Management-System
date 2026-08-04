from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework.response import Response
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, identity_code,phone=None, password=None ,**extra_fields):
        
        if not identity_code:
            raise ValueError("indentiry_code is required")

        if not phone:
            raise ValueError("phone is required")
        
        user = self.model(identity_code = identity_code, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, identity_code, password,phone, **extra_field):
        user = self.create_user(
            identity_code= identity_code,
            password = password,
            phone=phone,
            **extra_field
        )
        print(repr(phone))
        user.is_admin = True
        user.role = "admin"
        user.save(using=self._db)
        return user
    
# my customed user model
class User(AbstractBaseUser):
    Role_choice = [
        ("doctor", "Doctor"),
        ("patient", "Patient"),
        ("admin", "Admin")
    ]
    role = models.CharField(max_length=50, choices=Role_choice)
    fullname = models.CharField(max_length=100, null=True, blank=True)
    identity_code = models.CharField(max_length=10, unique=True)
    email=models.EmailField(unique=True, null=True, blank=True)
    phone=models.CharField(max_length=11)
    is_admin = models.BooleanField(default=False)
    
    

    objects = UserManager()

    USERNAME_FIELD = "identity_code"
    REQUIRED_FIELDS = ["phone"]

    

    def __str__(self):
        return f"{self.fullname} {self.identity_code}"

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    

        
    def is_doctor(self):
        if self.role == "doctor":
            return True
        return False

    def is_patient(self):
        if self.role == "patient":
            return True
        return False    
        

class Doctor(models.Model):

    SPECIALIZATION_CHOICES =[
        ('', '----------'),
        ('Dentistry', 'Dentistry'),
        ('Pharmacy', 'Pharmacy'),       
        ('Consultation', 'Consultation'),
        ('Flu Treatment', 'Flu Treatment'),
        ('ENT', 'Ear, Nose, and Throat (ENT)'),
        ('Reproductive Health', 'Reproductive Health'),
        ('Mental Health', 'Mental Health'),
        ('Physiotherapy', 'Physiotherapy'),
        ('Covid-Screening', 'Covid-19 Screening'),
        ('VCT', 'HIV Counselling & Treatment'),
        ('Laboratory', 'Laboratory Tests'),
        ('Referral', 'Referral'),
        ('Other issue', 'Other issue')
    ]
    specialization = models.CharField(max_length=60, choices=SPECIALIZATION_CHOICES, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor")
    image = models.ImageField(upload_to="media/image", null=True, blank=True) 

    

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient")
    father_name= models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to="media/image", null=True, blank=True)


class Otp(models.Model):
    phone = models.CharField(max_length=11)
    identity_code = models.CharField(max_length=10, default=0)
    token= models.CharField(max_length=200, unique=True)
    code = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)
    failed = models.BooleanField(default=False)  

    def __str__(self):
        return self.phone 

        

