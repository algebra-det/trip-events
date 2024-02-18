from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from misc.models import City, TravelType, TripInterest
from .serializers import TravelTypeSerializer, TripInterestSerializer, CitySerializer

class TravelTypeList(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:

            search = request.query_params.get('search', None)
            if search:
                travel_type = TravelType.objects.filter(title__icontains=search)
            else:
                travel_type = TravelType.objects.all()

            serialized = TravelTypeSerializer(travel_type, many=True)

            return Response({
                'status': True,
                'items': serialized.data
            })
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': 'Something Went Wrong!'
            }, status=404)


class TripInterestList(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:

            search = request.query_params.get('search', None)
            if search:
                trip_interest = TripInterest.objects.filter(title__icontains=search)
            else:
                trip_interest = TripInterest.objects.all()

            serialized = TripInterestSerializer(trip_interest, many=True)

            return Response({
                'status': True,
                'items': serialized.data
            })
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': 'Something Went Wrong!'
            }, status=404)


class CityList(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:

            search = request.query_params.get('search', None)
            if search:
                city = City.objects.filter(title__icontains=search)
            else:
                city = City.objects.all()

            serialized = CitySerializer(city, many=True)

            return Response({
                'status': True,
                'items': serialized.data
            })
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': 'Something Went Wrong!'
            }, status=404)

