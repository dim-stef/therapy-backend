from rest_framework import serializers
from accounts.models import User, UserProfile
from therapist.models import Therapist, TherapySession


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['name', 'is_therapist']


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    def get_profile(self, user):
        return UserProfileSerializer(user.profile).data

    class Meta:
        model = User
        fields = ['email', 'profile']


class TherapySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapySession
        fields = ['start_date', 'end_date']


class TherapistSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    sessions = serializers.SerializerMethodField()

    def get_profile(self, therapist):
        return UserProfileSerializer(therapist.user.profile).data

    def get_sessions(self, therapist):
        return TherapySessionSerializer(therapist.sessions.all(), many=True).data

    class Meta:
        model = Therapist
        fields = ['bio', 'profile', 'sessions']
