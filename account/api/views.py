from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics
from .serializers import UserSerializer, LoginSerializer, LogoutSerialzier, DoctorInfoSerializer, PatientInfoSerializer, RegisterLoginOtpSerializer, RegisterLoginOtpResponseSerializer, CheckOtpSerializer, CheckOtpResponseSerializer
from rest_framework_simplejwt.tokens import RefreshToken 
from account.models import User, Doctor, Patient
from django.contrib.auth import authenticate, login
import permissions.permissions as permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from appointment.api.paginations import SmallResultSetPagination
from rest_framework.filters import SearchFilter
from permissions.permissions import IsAdmin,DoctorOrAdminOrUserObject, AdminOrOwnerUser
from django.shortcuts import get_object_or_404



# this view registers user and generates jwt access and refresh tokens
class RegisterUserJwtView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            refresh_token = RefreshToken.for_user(user)
            data={
            "message":"user created successfully",
            "fullname": user.fullname,
            "email":user.email,
            "phone":user.phone,
            "identity_code": user.identity_code,
            "JWT_tokens":{
                "refresh_token":str(refresh_token),
                "access_token": str(refresh_token.access_token)
            }
            }
            return Response(data, status=status.HTTP_201_CREATED)


# this view registers user and generates auth token
class RegisterUserAuthTokenView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user = serializer.save()
            token, create = Token.objects.get_or_create(user = user)
            data = {
                "message":"user created successfully",
                "fullname":user.fullname if user.fullname else "Not entered",
                "phone":user.phone if user.phone else "Not entered",
                "identity_code": user.identity_code,
                "email":user.email if user.email else "Not entered",
                "AuthToken":token.key
            }
            return Response(data, status= status.HTTP_201_CREATED)
        
#this view generates jwt tokens to login with       
class LoginUserJwtVIew(APIView):
     def post(self, request):
          serializer = LoginSerializer(data = request.data, context={"request":request})
          if serializer.is_valid(raise_exception=True):
                user = serializer.validated_data.get("user")
                refresh_token = RefreshToken.for_user(user)
                data = {"JWT token":{
                "refresh_token": str(refresh_token),
                "access_token": str(refresh_token.access_token)
                }}
                
                return Response(data, status=status.HTTP_200_OK)
          else:
               return Response({"error":"invalid data"}, status=status.HTTP_401_UNAUTHORIZED)

# this view generates auth token to login with

class LoginUserAuthTokenView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data = request.data, context = {"request": request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data.get("user")
            token, create = Token.objects.get_or_create(user = user)
            data = {"AuthToken":token.key}
            return Response(data, status=status.HTTP_200_OK)

#create a view to generate an otp for user who has forgot the password or not registered 
class RegisterLoginOtp(generics.GenericAPIView):
    serializer_class = RegisterLoginOtpSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()
        response_serializer = RegisterLoginOtpResponseSerializer(otp)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

#create a view to check if code and token are in one otp object and login
class CheckOtp(generics.GenericAPIView):
    serializer_class = CheckOtpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data = request.data, context = {"token": request.headers.get("token")})
        serializer.is_valid(raise_exception=True)
        checked_otp = serializer.save()
        response_serializer = CheckOtpResponseSerializer(checked_otp)
        return Response({"message":"success", "data":response_serializer.data}, status=status.HTTP_200_OK)
        


#this view add jwt refresh token to blacklist
class LogoutJwtView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = LogoutSerialzier(data = request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save() 
            return Response({"message":"successfully logged out"}, status= status.HTTP_200_OK)
        return Response({"error":"invalid data"}, status = status.HTTP_400_BAD_REQUEST)

#this view deletes Authtoken
class LogoutAuthTokenView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message":"you logged out successfully"}, status=status.HTTP_200_OK)
    

# return list of users
class Users_list(generics.ListAPIView):
     queryset = User.objects.all().order_by("id")
     serializer_class = UserSerializer
     permission_classes = [IsAuthenticated,IsAdmin]
     pagination_class = SmallResultSetPagination
     filter_backends = [SearchFilter]
     search_fields = ["fullname"]

# returns an individual user by entering its pk in url
class User_detail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DoctorOrAdminOrUserObject] 
    

    def get_object(self):
        pk = self.kwargs.get("pk")
        user = get_object_or_404(User, pk=pk)


        self.check_object_permissions(self.request, user)
        return user
    
 
class UpdateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, AdminOrOwnerUser]

 
class DeleteAccountView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, permissions.IsOwner]



class CompleteProfile(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated, permissions.DoctorOrPatientToComplete]

    def get_object(self):
        
        if self.request.user.role == "doctor":
            
            doctor, created = Doctor.objects.get_or_create(user = self.request.user)
            return doctor

        elif self.request.user.role == "patient":

            patient, created = Patient.objects.get_or_create(user_id = self.request.user)
            return patient

        else:
            raise ValidationError({"error":"role of user not eather doctor or patient invalid"})  
          
        
    def get_serializer_class(self):
        if self.request.user.role == "doctor":
            return DoctorInfoSerializer
        elif self.request.user.role == "patient":
            return PatientInfoSerializer
    

class DoctorsListVIew(generics.ListAPIView):
    queryset = Doctor.objects.all().order_by("id")
    serializer_class = DoctorInfoSerializer
    permission_classes = [AllowAny]



class PatientListView(generics.ListAPIView):
    queryset = Patient.objects.all().order_by("id")
    serializer_class = PatientInfoSerializer
    permission_classes = [IsAuthenticated,IsAdmin]
    pagination_class = SmallResultSetPagination
    filter_backends = [SearchFilter]
    search_fields = ["fullname"]




    










        

    
        