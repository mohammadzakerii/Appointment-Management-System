from rest_framework import permissions

class IsDoctor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user.id == obj.doctor.user.id) 

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user.role == "patient")
        

class PatientOrAllowAny(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user.id == obj.patient.user.id) 

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True  

class DoctorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ["admin", "doctor"]               