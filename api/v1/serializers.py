import os
from rest_framework import serializers
from accounts.models import User, UserProfile
from therapist.models import Therapist, TherapySession, AvailableTimeRange
import stripe


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    def get_id(self, profile):
        return profile.surrogate

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'avatar', 'is_therapist', 'stripe_id', 'stripe_account_link',
                  'created', 'expires_at', 'charges_enabled']


class PublicUserProfileSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    def get_id(self, profile):
        return profile.surrogate

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'avatar']


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
            return TherapistWithSessionsSerializer(user.therapist).data
        return None

    class Meta:
        model = User
        fields = ['email', 'profile', 'therapist']


class TherapySessionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    therapist = serializers.SerializerMethodField()

    def get_user(self, session):
        return PublicUserProfileSerializer(session.user.profile).data

    def get_therapist(self, session):
        return TherapistSerializer(session.therapist).data

    class Meta:
        model = TherapySession
        fields = ['surrogate', 'user', 'therapist',
                  'start_date', 'end_date', 'status']


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
    availability_times = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_availability_times(self, therapist):
        return AvailableTimeRangeSerializer(therapist.available_time_ranges.all(), many=True).data

    def get_id(self, therapist):
        return therapist.surrogate

    def get_profile(self, therapist):
        return UserProfileSerializer(therapist.user.profile).data

    class Meta:
        model = Therapist
        fields = ['id', 'bio', 'profile', 'availability_times', 'status']


class TherapistWithSessionsSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    availability_times = serializers.SerializerMethodField()
    sessions = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_id(self, therapist):
        return therapist.surrogate

    def get_availability_times(self, therapist):
        return AvailableTimeRangeSerializer(therapist.available_time_ranges.all(), many=True).data

    def get_profile(self, therapist):
        return UserProfileSerializer(therapist.user.profile).data

    def get_sessions(self, therapist):
        return TherapySessionSerializer(therapist.sessions.all(), many=True).data

    class Meta:
        model = Therapist
        fields = ['id', 'bio', 'profile', 'sessions', 'availability_times', 'status']


class UpdateTherapistProfileSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance = super(UpdateTherapistProfileSerializer, self).update(instance, validated_data)
        return instance

    class Meta:
        model = Therapist
        fields = ['license', 'bio']


class AvailableTimeRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTimeRange
        fields = ['id', 'weekday', 'start_time', 'end_time']


class AvailableTimeRangeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTimeRange
        fields = ['weekday', 'start_time', 'end_time']


class ChangeAvailableTimesSerializer(serializers.Serializer):
    available_times = serializers.ListField(child=AvailableTimeRangeSimpleSerializer())

    def create(self, validated_data):
        therapist = Therapist.objects.get(surrogate=self.context.get('therapist'))

        if len(validated_data.get('available_times', [])) > 0:
            therapist.available_time_ranges.all().delete()
        for time_range in validated_data.get('available_times', []):
            AvailableTimeRange.objects.create(therapist=therapist, start_time=time_range.get('start_time'),
                                              end_time=time_range.get('end_time'), weekday=time_range.get('weekday'))
        return validated_data
