from django.db import models
from account.models import User,Doctor, Patient
from django.utils.translation import gettext_lazy as _

# Create your models here.



        
class Service(models.Model):
    name = models.CharField(max_length=100)
    slot_duration = models.DurationField()
    price = models.DecimalField(max_digits=10,decimal_places=3)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE , related_name="service")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)     

    def __str__(self):
        return f"{self.doctor.user.fullname} -{self.name}"   

class Appointment(models.Model):

    APPOINMENT_STATUS=[
        ("completed","Completed"),
        ("pending", "Pending"),
        ("scheduled", "Scheduled"),
        ("canceled", "Canceled")
    ]
    date = models.DateField()
    start_time = models.TimeField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointment")   
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointment") 
    status = models.CharField(max_length=55 ,choices= APPOINMENT_STATUS)
    service = models.ForeignKey(Service, on_delete = models.CASCADE, related_name="appointment")

    #meta data    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.doctor.user.fullname} - {self.date} -{self.start_time}"
    
DAYS_OF_WEEK = (
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
)
class WorkingHour(models.Model):
 
    start_work_time = models.TimeField()
    end_work_time = models.TimeField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="workinghour")
    days_of_week = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK, verbose_name="_Days of week")

    class Meta:
        constraints = [models.UniqueConstraint(fields= ["doctor", "days_of_week"], name="unique working hour per day")]

    def __str__(self):
        return f" {self.doctor.user.fullname} - start_work_time{self.start_work_time} - day of week {self.get_days_of_week_display()}"

class Payment(models.Model):
    is_paid = models.BooleanField(default=False)
    amount_to_pay = models.DecimalField(max_digits=10,decimal_places=3, default=0)
    down_payment = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="payment")
    authority = models.CharField(max_length=100, null=True, blank=True)
    ref_id = models.CharField(max_length=100, null=True, blank=True)
    card_num = models.CharField(null=True, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True , null=True)

    def __str__(self):
        return f"{self.appointment.doctor.user.fullname}-{self.appointment.service}-{self.appointment.date}-{self.appointment.start_time} remaining amount is {self.remaining_amount}"

