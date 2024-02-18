from rest_framework import serializers
from misc.models import TravelType, TripInterest, City

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        exclude = ('created_at', 'updated_at')

class TravelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelType
        exclude = ('created_at', 'updated_at')

class TripInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripInterest
        exclude = ('created_at', 'updated_at')