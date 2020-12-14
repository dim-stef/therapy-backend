from rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_framework import serializers
from .models import UserProfile


class RegistrationSerializer(RegisterSerializer):
    is_therapist = serializers.BooleanField(required=False, write_only=True)
    name = serializers.CharField(required=True, write_only=True, max_length=60)

    def get_cleaned_data(self):
        return {
            'is_therapist': self.validated_data.get('is_therapist', ''),
            'name': self.validated_data.get('name', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user_profile = UserProfile.objects.create(user=user,
                                                  is_therapist=self.cleaned_data.get('is_therapist', False),
                                                  name=self.cleaned_data.get('name', ''))
        user.save()
        return user
