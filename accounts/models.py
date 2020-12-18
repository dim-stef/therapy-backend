from django.db import models
from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
import uuid


class User(AbstractUser):
    class Meta:
        swappable = "AUTH_USER_MODEL"
        db_table = "auth_user"

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'
    username = models.CharField(blank=False, null=False, max_length=30)
    email = models.EmailField(unique=True, db_index=True)
    surrogate = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True)


class UserProfile(models.Model):
    surrogate = models.UUIDField(default=uuid.uuid4, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(blank=False, null=False, max_length=60, default="")
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
    is_therapist = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=40, null=True, blank=True)
    stripe_account_link = models.URLField(blank=True, null=True)
    created = models.IntegerField(null=True, blank=True)
    expires_at = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} - {self.name}'
