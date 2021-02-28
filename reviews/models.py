from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from accounts.models import User
from therapist.models import Therapist
import uuid

# Create your models here.
class Review(models.Model):
    surrogate = models.UUIDField(default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name="reviews")
    stars = models.IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['user', 'therapist'], name='unique_user_review')
    ]
