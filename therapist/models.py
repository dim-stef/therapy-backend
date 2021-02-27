from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from djmoney.models.fields import MoneyField
from accounts.models import User
import uuid
from datetime import timedelta, datetime


class Therapist(models.Model):

    ACTIVE = 'AC'
    INACTIVE = 'IN'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]

    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=INACTIVE
    )

    surrogate = models.UUIDField(default=uuid.uuid4, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="therapist")
    bio = models.TextField(null=True, blank=True, max_length=300)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    office_number = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=160, blank=True, null=True)
    afm = models.CharField(max_length=60, blank=True, null=True)
    doy = models.CharField(max_length=300, blank=True, null=True)
    iban = models.CharField(max_length=40, blank=True, null=True)
    license = models.ImageField(upload_to='licenses/', null=True, blank=True)
    id_back = models.ImageField(upload_to='id/', null=True, blank=True)
    id_front = models.ImageField(upload_to='id/', null=True, blank=True)
    credit = MoneyField(max_digits=6, decimal_places=2, default_currency='EUR', default=0.0)

    def __str__(self):
        return str(self.user.email)

    class Meta:
        ordering = ('created',)


class TherapistSpecialties(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name="specialties")
    specialty = models.CharField(max_length=50)

    def __str__(self):
        return self.specialty


class TherapySession(models.Model):
    APPROVED = 'AC'
    REJECTED = 'RJ'
    PENDING = 'PD'
    PAYMENT_COMPLETED = 'PC'

    STATUS_CHOICES = [
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending'),
        (PAYMENT_COMPLETED, 'Payment completed')
    ]

    surrogate = models.UUIDField(default=uuid.uuid4, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, null=False, blank=False, related_name="sessions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="sessions")
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.end_date = self.start_date + timedelta(hours=1)
        super(TherapySession, self).save(*args, **kwargs)

    def __str__(self):
        return self.therapist.user.email + ' - ' + str(self.start_date)


class AvailableTimeRange(models.Model):
    WEEKDAYS = [
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    ]

    weekday = models.IntegerField(choices=WEEKDAYS)
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name="available_time_ranges")
    start_time = models.TimeField()
    end_time = models.TimeField()


@receiver(post_save, sender=TherapySession)
def save_therapy_session(sender, instance, created, **kwargs):
    if created:
        pass#instance.profile.save()
