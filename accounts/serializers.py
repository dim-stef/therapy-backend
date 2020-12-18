import os
from django.contrib.sites.models import Site
from django.conf import settings
from rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_framework import serializers
from therapist.models import Therapist
from .models import UserProfile
import stripe


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

        if self.cleaned_data.get('is_therapist', False):
            Therapist.objects.create(user=user, bio=self.cleaned_data.get('bio', ''))
        account = setup_stripe_account(user, user_profile)

        user_profile.save()
        user.save()
        return user


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
