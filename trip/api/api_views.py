from django.db.models.query_utils import refs_expression
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from account.models import MyUser

from migo.utils.images_to_dict import modify_input_for_multiple_files

from .serializers import TripCreateSerializer, PlannerCreateSerializer, TripDetailsSerializer, TripLogSerializer, TripLogImageSerializer
from trip.models import Planner, Trip

from stay.models import PlannerWishlist, Stay
from trip.utils.checkDate import check_trip_type_via_start_date

class TripCreateAPIView(APIView):

    def post(self, request):
        serializer = TripCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": True,
            "message": "Trip Created successfully, Please add a planner now.",
            "data": serializer.data
        })

class TripDetailAPIView(APIView):

    def get(self, request, trip_id):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({
                "status": False,
                "message": "No Trip Found with this trip_id"
            }, status=400)
        
        serializer = TripDetailsSerializer(trip)
        return Response({
            "status": True,
            "data": serializer.data
        })

class PlannerCreateAPIView(APIView):

    def post(self, request):
        trip_id: int = request.data.get('trip')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        wishlist_stays = request.data.get('wishlist_stays')
        wishlist_events = request.data.get('wishlist_events')

        if not trip_id:
            return Response({
                "status": False,
                "message": "trip is required which have value of trip id",
                "field": "trip"
            }, status=400)
        
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({
                "status": False,
                "message": "No trip found with this ID",
                "field": "trip"
            }, status=400)
        
        user = request.user
        trips = Trip.objects.filter(Q(members__id=user.id) | Q(user=user))
        for t in trips:
            planner_coexists = t.planners.filter(Q(start_date__gte=start_date) & Q(end_date__lte=end_date))
            if planner_coexists.exists():
                return Response({
                    "status": False,
                    "message": f"Planner exists for such period of time in {t} starting on {t.start_date} and ending on {t.end_date}",
                }, status=400)


        if trip.user != user:
            return Response({
                "status": False,
                "message": "Only Trip creator can add planners.",
            }, status=400)
        
        serializer = PlannerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if wishlist_stays:
            try:
                pass
            except Exception as e:
                print(e)
                return Response({
                    "status": False,
                    "message": "Error Occured while processing wishlist_stays, make sure it's an array and have proper IDs"
                })


        return Response({
            "status": True,
            "message": "Planner added successfully.",
            "data": serializer.data
        })
        

class PlannerDetailsAPIView(APIView):

    def get(self, request, planner_id):
        try:
            planner = Planner.objects.get(id=planner_id)
        except Planner.DoesNotExist:
            return Response({
                "status": False,
                "message": "Planner not found with this planner_id"
            }, status=400)
        
        serializer = PlannerCreateSerializer(planner)
        return Response({
            "status": True,
            "message": "Planner Found!",
            "data": serializer.data
        })

class TripPlannerListingAPIView(APIView):

    def get(self, request, trip_id):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({
                "status": False,
                "message": "Trip not found with this trip_id"
            }, status=400)
        
        planners = Planner.objects.filter(trip=trip)
        serializer = PlannerCreateSerializer(planners, many=True)
        return Response({
            "status": True,
            "data": serializer.data,
            "message": "No planners found!" if not planners.exists() else "Planners found!"
        })


class AddMemberToTripAPIView(APIView):

    def post(self, request):
        try:
            trip_id = request.data['trip']
            user_id = request.data['user']
            trip = Trip.objects.get(pk=trip_id)
            user = MyUser.objects.get(pk=user_id)

            if trip.user != request.user:
                return Response({
                    "status": False,
                    "message": "You Are Not Authorized!"
                }, status=400)

            if not check_trip_type_via_start_date(trip.start_date):
                return Response({
                    "status": False,
                    "message": "Can't Add Any user now!"
                }, status=400)
            
            if trip.members.all().count() >= trip.number_of_travellers:
                return Response({
                    "status": False,
                    "message": "Trip members full!"
                    }, status=400)

            if user not in trip.members.all():
                trip.members.add(user)
                return Response({
                    "status": True,
                    "message": "User Added in Trip!"
                })
            else:
                return Response({
                    "status": False,
                    "message": "User Already added in Trip!"
                }, status=400)
        except Trip.DoesNotExist or MyUser.DoesNotExist:
            return Response({
                "status": False,
                "message": "trip_id & user_id is required!"
            }, status=400)


class RemoveMemberToTripAPIView(APIView):

    def post(self, request):
        try:
            trip_id = request.data['trip']
            user_id = request.data['user']
            trip = Trip.objects.get(pk=trip_id)
            user = MyUser.objects.get(pk=user_id)

            if trip.user != request.user:
                return Response({
                    "status": False,
                    "message": "You Are Not Authorized!"
                }, status=400)

            if not check_trip_type_via_start_date(trip.start_date):
                return Response({
                    "status": False,
                    "message": "Can't remove Any user now!"
                }, status=400)
            
            if user in trip.members.all():
                trip.members.remove(user)
                return Response({
                    "status": True,
                    "message": "User Removed in Trip!"
                })
            else:
                return Response({
                    "status": False,
                    "message": "User Already not in Trip!"
                }, status=400)
        except Trip.DoesNotExist or MyUser.DoesNotExist:
            return Response({
                "status": False,
                "message": "trip_id & user_id is required!"
            }, status=400)

            
class TripLogCreateAPIView(APIView):

    def post(self, request):
        trip_id = request.data.get('trip')
        files = dict((request.data).lists()).get('files')

        if not trip_id:
            return Response({
                "status": False,
                "message": "trip is required!"
            }, status=400)
        
        try:
            trip = Trip.objects.get(id=trip_id)
        except Exception as e:
            return Response({
                "status": False,
                "message": "No Trip Found with given trip ID."
            }, status=400)
        
        user = request.user
        if trip.user != user and user not in trip.members.all():
            return Response({
                "status": False,
                "message": "You are not a part of this trip."
            }, status=400)
        

        final_response = {}

        if files and len(files):

            log_serializer = TripLogSerializer(data=request.data, context={"request": request})
            log_serializer.is_valid(raise_exception=True)
            log_serializer.save()

            final_response.update(log_serializer.data)


            files_arr = []
            for single_file in files:
                modified_data = modify_input_for_multiple_files('log',log_serializer.data['id'], single_file, 'log_file')
                print("modified serializer: ", modified_data)
                file_serializer = TripLogImageSerializer(data=modified_data)
                file_serializer.is_valid(raise_exception=True)
                file_serializer.save()
                print("file serializer: ", modified_data)
                files_arr.append(file_serializer.data)

            final_response.update({
                "files": files_arr
            })

            return Response({
                "status": True,
                "message": "Trip Log Created Successfully!",
                "data": final_response
            }, status=400)
        
        else:
            return Response({
                "status": False,
                "message": "files array of files is required."
            }, status=400)

