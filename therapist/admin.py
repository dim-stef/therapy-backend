from django.contrib import admin
from .models import Therapist, TherapySession, AvailableTimeRange

# Register your models here.
admin.site.register(Therapist)
admin.site.register(TherapySession)
admin.site.register(AvailableTimeRange)
