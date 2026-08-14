from rest_framework import permissions

class ReadOnlyOrOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif not request.user.is_authenticated:
            return False
        else:
            return bool(request.user.id == obj.doctor.user.id or request.user.role == "admin" ) 

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user.role == "patient")

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
            return obj.id == request.user.id


class DoctorOrPatientToComplete(permissions.BasePermission):
      def has_object_permission(self, request, view, obj):
            return obj.user.id == request.user.id         
        

class ReadOnlyOrPatient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user.id == obj.patient.user.id) 

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_admin:
            return True 

     

class ReadOnlyOrDoctorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True 
        else:
            return (
                request.user.is_authenticated and
                request.user.role in ["admin", "doctor"])

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True 
        else:
            return (
                request.user.is_authenticated and

                (request.user.role == "doctor" and obj.doctor.id == request.user.doctor.id or
                request.user.role == "admin") )

class OwnerDoctorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == "doctor" and obj.doctor.id == request.user.doctor.id or request.user.role == "admin"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role =="admin":
            return True
        if request.user.role == "doctor":
            doctor_id = view.kwargs.get("doctor_id")
            if request.user.doctor.id == int(doctor_id):
                return True
        else:    
            return False  
    

class DoctorOrAdminOrUserObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
         return obj.id == request.user.id or request.user.role in ["admin", "doctor"]  

class AdminOrOwnerUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id or request.user.role == "admin"

class DoctorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role=="doctor" or request.user.role=="admin"

class OwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ["admin", "patient"])

    def has_object_permission(self, request, view, obj):
        if request.user.role =="admin": 
            return True
        
        elif obj.patient.id == request.user.patient.id:
            return True
        else:
            return False

class OwnerUserOrDoctorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if not request.user.is_authenticated:
            return False
        
        if request.user.role in ["doctor", "admin"]:
            return True 
        
        if request.user.role == "patient":
            patient_id = view.kwargs.get("patient_id")
            return request.user.patient.id == int(patient_id)
        
        return False     

   
class OwnerPatientOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "admin":
            return True
        if request.user.role == "patient":
            patient_id = view.kwargs.get("patient_id")
            return request.user.patient.id == int(patient_id)
            
        
                
                     
    