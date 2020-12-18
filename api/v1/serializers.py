import os
from rest_framework import serializers
from accounts.models import User, UserProfile
from therapist.models import Therapist, TherapySession
import stripe


class UserProfileSerializer(serializers.ModelSerializer):
    charges_enabled = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_id(self, profile):
        return profile.surrogate

    def get_charges_enabled(self, profile):
        if profile.stripe_id:
            stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
            account = stripe.Account.retrieve(profile.stripe_id)
            return account.charges_enabled
        return None

    class Meta:
        model = UserProfile
        fields = ['id','name', 'avatar', 'is_therapist', 'stripe_id', 'stripe_account_link',
                  'created', 'expires_at', 'charges_enabled']


class UpdateUserProfileSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance = super(UpdateUserProfileSerializer, self).update(instance, validated_data)
        return instance

    class Meta:
        model = UserProfile
        fields = ['name', 'avatar']


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    therapist = serializers.SerializerMethodField()

    def get_profile(self, user):
        return UserProfileSerializer(user.profile).data

    def get_therapist(self, user):
        if user.profile.is_therapist:
            return TherapistSerializer(user.therapist).data
        return None

    class Meta:
        model = User
        fields = ['email', 'profile', 'therapist']


class TherapySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapySession
        fields = ['start_date', 'end_date']


class CreateTherapySessionSerializer(serializers.ModelSerializer):
    therapist = serializers.UUIDField(required=True)

    def create(self, validated_data):
        user = self.context.get('user')
        try:
            therapist_surrogate = validated_data.pop('therapist')
        except KeyError:
            therapist_surrogate = None

        therapist = Therapist.objects.get(surrogate=therapist_surrogate)
        instance = TherapySession.objects.create(user=user, therapist=therapist, **validated_data)
        return instance

    class Meta:
        model = TherapySession
        fields = ['start_date', 'therapist']
        read_only_fields = ['end_date', 'user']


class TherapistSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    sessions = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_id(self, therapist):
        return therapist.surrogate

    def get_profile(self, therapist):
        return UserProfileSerializer(therapist.user.profile).data

    def get_sessions(self, therapist):
        return TherapySessionSerializer(therapist.sessions.all(), many=True).data

    class Meta:
        model = Therapist
        fields = ['id', 'bio', 'profile', 'sessions']
