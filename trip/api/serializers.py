from django.db import models
from core.api.serializers import StayHostSerializer
from rest_framework import serializers

from trip.models import Log, LogFiles, Trip, Planner

class TripCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Trip
        fields = ('id', 'creator', 'user', 'title', 'trip_type', 'type_of_travel', 'number_of_travellers')

class TripDetailsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = ('title', 'owner', 'content')

    def get_owner(self, trip):
        serializer = StayHostSerializer(trip.user.profile)
        return serializer.data
    
    def get_content(self, trip):
        planners = Planner.objects.filter(trip=trip)
        if planners.exists():
            return planners.first().note
        else:
            return ""

class PlannerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Planner
        fields = "__all__"
        extra_kwargs = {
            'stay_budget': {'required': True},
            'transport_budget': {'required': True},
            'event_budget': {'required': True},
            'activity_budget': {'required': True},
        }
    
    # def validate(self, attrs):
    #     if not attrs.get('stay_budget'):
    #         raise serializers.ValidationError({"stay_budget": ["stay_budget is required."]})
    #     if not attrs.get('transport_budget'):
    #         raise serializers.ValidationError({"transport_budget": ["transport_budget is required."]})
    #     if not attrs.get('event_budget'):
    #         raise serializers.ValidationError({"event_budget": ["event_budget is required."]})
    #     if not attrs.get('activity_budget'):
    #         raise serializers.ValidationError({"activity_budget": ["activity_budget is required."]})
    #     return super().validate(attrs)

class TripLogSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Log
        exclude = ('updated_at',)


class TripLogImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = LogFiles
        fields = ('id', 'log', 'log_file')