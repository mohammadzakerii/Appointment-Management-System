from django.urls import path
from . import views
app_name = "account"

urlpatterns = [
path("register_jwt/", views.RegisterUserJwtView.as_view(), name="register_jwt"),
path("register_authtoken/",views.RegisterUserAuthTokenView.as_view(), name="register_authtoken" ),
path("login_jwt/", views.LoginUserJwtVIew.as_view(), name="login_user"),
path("login_authtoken", views.LoginUserAuthTokenView.as_view(), name = "login_authtoken"),
path("register_login_otp", views.RegisterLoginOtp.as_view(), name="register_login_otp"),
path("check_otp", views.CheckOtp.as_view(), name="check_otp"),
path("logout_jwt", views.LogoutJwtView.as_view(), name="logout_jwt"),
path("logout_authtoken", views.LogoutAuthTokenView.as_view(), name="logout_authtoken"),
path("list/", views.Users_list.as_view(), name="user_list"),
path("detail/<int:pk>", views.User_detail.as_view(), name="user_detail"),
path("update/<int:pk>", views.UpdateUserView.as_view(), name="update_user"),
path("delete/<int:pk>", views.DeleteAccountView.as_view(), name="delete"),
path("complete_profile/", views.CompleteProfile.as_view(), name="complete_profile"),
path("doctor_list", views.DoctorsListVIew.as_view(), name="doctor_list"),
path("patient_list", views.PatientListView.as_view(), name="patient_list")
]