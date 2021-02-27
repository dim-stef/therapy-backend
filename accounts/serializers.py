import os
from django.contrib.sites.models import Site
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from django.utils.translation import gettext as _
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import PasswordResetSerializer, PasswordResetConfirmSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_framework import serializers
from therapist.models import Therapist, TherapistSpecialties
from .models import UserProfile, User
import stripe


class RegistrationSerializer(RegisterSerializer):
    is_therapist = serializers.BooleanField(required=False, write_only=True)
    name = serializers.CharField(required=True, write_only=True, max_length=60)
    bio = serializers.CharField(max_length=300, write_only=True, required=False)
    office_number = serializers.CharField(max_length=300, write_only=True, required=False)
    phone_number = serializers.CharField(max_length=300, write_only=True, required=False)
    address = serializers.CharField(max_length=300, write_only=True, required=False)
    # specialties come as a comma separated string
    specialties = serializers.CharField(max_length=1000, write_only=True, required=False)

    def get_cleaned_data(self):
        print(self.validated_data)
        return {
            'is_therapist': self.validated_data.get('is_therapist', ''),
            'name': self.validated_data.get('name', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'bio': self.validated_data.get('bio', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'office_number': self.validated_data.get('office_number', ''),
            #'specialisation': self.validated_data.get('specialisation', ''),
            'address': self.validated_data.get('address', ''),
            'specialties': self.validated_data.get('specialties', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])

        if self.cleaned_data.get('is_therapist', False):
            is_therapist = True
        else:
            is_therapist = False
        user_profile = UserProfile.objects.create(user=user,
                                                  is_therapist=is_therapist,
                                                  name=self.cleaned_data.get('name', ''))

        if is_therapist:
            therapist = Therapist.objects.create(user=user, bio=self.cleaned_data.get('bio', ''),
                                                 phone_number=self.validated_data.get('phone_number', ''),
                                                 office_number=self.validated_data.get('office_number', ''),
                                                 address=self.validated_data.get('address', ''))
            specialties = self.validated_data.get('specialties', '').split(",")
            for specialty in specialties:
                TherapistSpecialties.objects.create(therapist=therapist, specialty=specialty)

            # only handling stripe accounts for therapists for now
            # TODO run this again in case of migration from regular account -> therapist account
            account = setup_stripe_account(user, user_profile)

        user_profile.save()
        user.save()
        return user


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        return {
            'html_email_template_name': 'registration/'
                                    'password_reset_message.html',
            'extra_email_context': {
                'frontend_url': 'https://%s' % (Site.objects.get_current().domain),
            }
        }

class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    def get_email_options(self):
        return {
            'html_email_template_name': 'registration/'
                                    'password_reset_message.html',
            'extra_email_context': {
                'frontend_url': 'https://%s' % (Site.objects.get_current().domain),
            }
        }

def setup_stripe_account(user, user_profile):
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

    account = stripe.Account.create(
        type="express",
        country="GR",
        email=user.email,
        capabilities={
            "card_payments": {"requested": True},
            "transfers": {"requested": True},
        },
    )

    if settings.DEBUG:
        redirect = 'http://localhost:3000/users/oauth/callback'
        refresh_url = "http://localhost:3000/reauth"
    else:
        redirect = 'https://%s%s' % (Site.objects.get_current().domain, '/users/oauth/callback')
        refresh_url = 'https://%s%s' % (Site.objects.get_current().domain, '/reauth')

    account_link = stripe.AccountLink.create(
        account=account.id,
        refresh_url=refresh_url,
        return_url=redirect,
        type="account_onboarding",
    )

    user_profile.stripe_id = account.id
    user_profile.stripe_account_link = account_link.url
    user_profile.created = account_link.created
    user_profile.expires_at = account_link.expires_at
    user_profile.save()
    return account_link
