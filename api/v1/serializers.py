import os
from rest_framework import serializers
from django.db.models import Avg
from accounts.models import User, UserProfile
from reviews.models import Review
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
    specialties = serializers.StringRelatedField(many=True)
    availability_times = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_availability_times(self, therapist):
        return AvailableTimeRangeSerializer(therapist.available_time_ranges.all(), many=True).data

    def get_id(self, therapist):
        return therapist.surrogate

    def get_profile(self, therapist):
        return UserProfileSerializer(therapist.user.profile).data

    def get_review(self, therapist):
        user = self.context.get('user')
        if user and user.is_authenticated:
            review = Review.objects.filter(user=user, therapist=therapist)
            if review.exists():
                return ReviewSerializer(review.first()).data
        return None

    def get_reviews(self, therapist):
        average_rating = therapist.reviews.all().aggregate(Avg('stars'))['stars__avg']
        rating_count = therapist.reviews.count()
        return {'average_rating': average_rating, 'count': rating_count}

    class Meta:
        model = Therapist
        fields = ['id', 'bio', 'profile', 'phone_number', 'office_number', 
        'address', 'credit', 'availability_times', 'status', 'specialties', 'review', 'reviews']


class TherapistWithSessionsSerializer(serializers.ModelSerializer):
    specialties = serializers.StringRelatedField(many=True)
    profile = serializers.SerializerMethodField()
    availability_times = serializers.SerializerMethodField()
    sessions = serializers.SerializerMethodField()
    review = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_id(self, therapist):
        return therapist.surrogate

    def get_availability_times(self, therapist):
        return AvailableTimeRangeSerializer(therapist.available_time_ranges.all(), many=True).data

    def get_profile(self, therapist):
        return UserProfileSerializer(therapist.user.profile).data

    def get_sessions(self, therapist):
        return TherapySessionSerializer(therapist.sessions.all(), many=True).data

    def get_review(self, therapist):
        user = self.context.get('user')
        if user and user.is_authenticated:
            review = Review.objects.filter(user=user, therapist=therapist)
            if review.exists():
                return ReviewSerializer(review.first()).data
        return None

    def get_reviews(self, therapist):
        average_rating = therapist.reviews.all().aggregate(Avg('stars'))['stars__avg']
        rating_count = therapist.reviews.count()
        return {'average_rating': average_rating, 'count': rating_count}

    class Meta:
        model = Therapist
        fields = ['id', 'bio', 'profile', 'phone_number', 'office_number', 'address', 'credit', 
        'sessions', 'availability_times', 'status', 'specialties', 'review', 'reviews']


class ReviewSerializer(serializers.ModelSerializer):
    therapist = serializers.UUIDField(required=True)
    id = serializers.SerializerMethodField()

    def get_id(self, review):
        return review.surrogate

    def create(self, validated_data):
        user = self.context.get('user')
        try:
            therapist_surrogate = validated_data.pop('therapist')
        except KeyError:
            therapist_surrogate = None

        therapist = Therapist.objects.get(surrogate=therapist_surrogate)
        instance = Review.objects.create(user=user, therapist=therapist, **validated_data)
        return instance

    def update(self, instance, validated_data):
        try:
            therapist_surrogate = validated_data.pop('therapist')
        except KeyError:
            therapist_surrogate = None

        therapist = Therapist.objects.get(surrogate=therapist_surrogate)
        instance.therapist = therapist
        instance = super(ReviewSerializer, self).update(instance, validated_data)
        return instance

    class Meta:
        model = Review
        fields = ['therapist', 'user', 'stars', 'id']
        read_only_fields = ['user', 'id']


class UpdateTherapistProfileSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance = super(UpdateTherapistProfileSerializer, self).update(instance, validated_data)
        return instance

    class Meta:
        model = Therapist
        fields = ['license', 'id_back', 'id_front', 'afm', 'doy', 'iban', 'bio']


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
