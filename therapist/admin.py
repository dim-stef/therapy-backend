from django.contrib import admin
from .models import Therapist, TherapySession

# Register your models here.
admin.site.register(Therapist)
admin.site.register(TherapySession)
