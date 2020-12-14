from django.db import models
from accounts.models import User
import uuid
from datetime import timedelta


class Therapist(models.Model):
    surrogate = models.UUIDField(default=uuid.uuid4, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="therapist")
    bio = models.TextField(null=True, blank=True, max_length=300)


class TherapySession(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, null=False, blank=False, related_name="sessions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="sessions")
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.end_date = self.start_date + timedelta(hours=1)
        super(TherapySession, self).save(*args, **kwargs)
