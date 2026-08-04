from django.contrib import admin
from .models import Appointment, Service, WorkingHour, Payment
# Register your models here.

admin.site.register(Appointment)
admin.site.register(Service)
admin.site.register(WorkingHour)
admin.site.register(Payment)