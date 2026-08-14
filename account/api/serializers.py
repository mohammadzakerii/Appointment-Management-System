from rest_framework import serializers
from account.models import User, Doctor, Patient,Otp
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from datetime import timedelta
from django.utils import timezone
from django.utils.crypto import get_random_string
from random import randint
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


class DoctorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["specialization", "bio", "image","id"]

class PatientInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["father_name", "image","id"] 

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = User
        fields= ["identity_code", "password","password2", "phone", "email", "fullname", "role" , "id","profile","is_admin"]
        read_only_fields= ["id"]
        extra_kwargs = {
            'password': {'write_only' : True},
            'email':{"required" :False},
            "fullname":{"required":  False},
        }

    #check the role of user to display some info of specefied role
    def get_profile(self, obj):
        if obj.role == "doctor":
            return DoctorInfoSerializer(obj.doctor).data
        elif obj.role == "patient":
            return PatientInfoSerializer(obj.patient).data
        return None  
      
    #to check if value is numeric 
    def validate_identity_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("identity code must contain only numbers")
    
    #to check len of value    
        if len (value) != 10:
            raise serializers.ValidationError("identity code should have 10 number charactors")
    
    # to check if value is not unique    
        elif User.objects.filter(identity_code = value).exists():
            raise serializers.ValidationError("not unique identity code")
        
        return value

    def validate_phone(self, value):

        #to check if value is numeric
        if not value.isdigit():
            raise serializers.ValidationError("phone number must contain only numbers")
        
        #to check if value starts with 09
        if not value.startswith("09"):
            raise serializers.ValidationError("phone number should start with 09")
        
        #to check len of value
        elif len(value) != 11:
            raise serializers.ValidationError("phone number should have 11 numeric charactor")

        return value

    #to check if passwords are not the same           
    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password or password2:
            if attrs["password"] != attrs["password2"]:
                raise serializers.ValidationError("passwords are not the same")
        
        return attrs    
    
    #using customized create method to check the role and create a doctor or patient object for user related to its role
    def create(self, validated_data):

        validated_data.pop("password2")
        
        role = validated_data.pop("role")

        user_obj = User.objects.create_user(role=role, **validated_data)

        if role == "doctor":
            Doctor.objects.create(user = user_obj)

        if role == "patient":
            Patient.objects.create(user = user_obj)

        return user_obj
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("password2", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            if password:
                instance.set_password(password)
                instance.save()

        return instance
    


     
            
class LoginSerializer(serializers.Serializer):
    identity_code = serializers.CharField()
    password = serializers.CharField()

    def validate_identity_code(self, value):
        #to check if identity_code contains just 10 charaters
        if len(value)!= 10:
            raise serializers.ValidationError("identity_code must have 10 numeric characters")

        #check to make sure that identity_code is numeric
        if not value.isdigit():
            raise serializers.ValidationError("identity code must contain only numbers")
        
        
        return value
    
    def validate(self ,attrs):
        request = self.context["request"]

        if request and request.user.is_authenticated:
            raise serializers.ValidationError("you are already authenticated ")
        
        user = authenticate(request, identity_code= attrs["identity_code"], password = attrs["password"] )

        if user is None:
            raise serializers.ValidationError("identity_code or password are not correct")
        
        attrs["user"] = user
        return attrs

class RegisterLoginOtpSerializer(serializers.Serializer):
    identity_code = serializers.CharField(max_length=10)
    phone = serializers.CharField(max_length=11)

    def validate_identity_code(self, value):
        if len (value) != 10:
            raise serializers.ValidationError("identity code should contans only 10 numeric characters")
        if not value.isdigit():
            raise serializers.ValidationError("identity_code should only contains numeric charaters")
        return value
    
    def validate_phone(self, value):
        if len(value) != 11:
            raise serializers.ValidationError("phone number should caontains 11 nueric charactors")
        if not value.isdigit():
            raise serializers.ValidationError("phone number should only contains numeric charactors")
        return value
        
    def validate(self, attrs):
        phone = attrs["phone"]
       
        #to make sure that phone is entered
        if phone is None:
            raise serializers.ValidationError("you havnt added a phone number")
        
        today = timezone.now().date()

        #every user can have 5 request for otp per day
        failed_count = Otp.objects.filter(phone = phone, created_at__date=today).count()
        if failed_count >= 5:
            raise serializers.ValidationError("daily limit reached")

        #two minutes should spent if user wants to request for otp again
        last_otp = Otp.objects.filter(phone = phone).order_by("-created_at").first()
        if last_otp:
            if timezone.now() - last_otp.created_at < timedelta(minutes=2):
                raise serializers.ValidationError("next otp will be sent after 2 minutes")
            
        return attrs
    
    def create(self, validated_data):
        identity_code = validated_data["identity_code"]
        phone = validated_data["phone"]

        token = get_random_string(length=100)
        code = randint(1000,9999)
        print(f"token : {token}")
        print(f"code : {code}")
        otp = Otp.objects.create(phone=phone,identity_code = identity_code,token=token, code=code)
        return otp
    
class RegisterLoginOtpResponseSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=200)

class CheckOtpSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(slef, value):
        #code should have 4 characters
        if len(value) != 4 :
            raise serializers.ValidationError("code should contains 4 number characters")
        
        
        return value
    
    def validate(self, attrs):
        token = self.context["token"]
        code = attrs["code"]
       

        try:
            otp = Otp.objects.get(token= token)

        except Otp.DoesNotExist:
            raise serializers.ValidationError("something went wrong please try again")

        #if user enters wrong code for 5 times otp needs to be requested again
        if otp.attempts >= 5:
            raise serializers.ValidationError("too many attemps request for otp again ")
        
        #validation time for otp is 2 minutes after that user needs to request again to generate new otp 
        if timezone.now() - otp.created_at > timedelta(minutes=2):
            otp.failed = True
            raise serializers.ValidationError("validation time expired please request again")


        if str(code) != str(otp.code):
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            raise serializers.ValidationError("code is wrong")
        
        self.otp = otp

        
        return attrs

    def create(self, validated_data):
        otp = self.otp

        #check if user exists if not we create new one 
        try:
            user = User.objects.get(identity_code = otp.identity_code)

            if user.phone != otp.phone:
                raise serializers.ValidationError(f"user with identity code {user.identity_code} has another phone number")

        except  User.DoesNotExist:
            user = User.objects.create(identity_code = otp.identity_code, phone = otp.phone)    


        refresh_token = RefreshToken.for_user(user)
        auth_token, is_created = Token.objects.get_or_create(user = user)

        
        return {"refresh_token":refresh_token,"access_token":refresh_token.access_token, "auth_token":auth_token.key}

class CheckOtpResponseSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=100)
    access_token = serializers.CharField(max_length=100)
    auth_token = serializers.CharField(max_length=50)    
        


class LogoutSerialzier(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs["refresh_token"]
        
        try:
            attrs["token"] = RefreshToken(refresh_token)
        except TokenError:
            raise serializers.ValidationError("refresh token is invalid, expired or already blacklisted")    
   
        return attrs
    
    def save(self):
        token = self.validated_data["token"]
        token.blacklist()