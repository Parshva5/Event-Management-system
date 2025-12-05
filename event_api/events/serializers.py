from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile, Event, RSVP, Review


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "full_name", "bio", "location", "profile_picture"]


class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "organizer",
            "location",
            "start_time",
            "end_time",
            "is_public",
            "invited_users",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["organizer", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["organizer"] = request.user
        return super().create(validated_data)


class RSVPSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RSVP
        fields = ["id", "event", "user", "status"]
        read_only_fields = ["event", "user"]

    def validate_status(self, value):
        if value not in dict(RSVP.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid RSVP status.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "event", "user", "rating", "comment", "created_at"]
        read_only_fields = ["event", "user", "created_at"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
