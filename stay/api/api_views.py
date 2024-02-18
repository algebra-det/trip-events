
from os import EX_CANTCREAT, environ
import datetime

from rest_framework import serializers
from rest_framework import response
from stay.utils.save_facilities import save_facilities
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from migo.utils.customPermissionClass import NotDjangoAdmin, SignUpProcessCompleted, IsHost
import json
from django.db import connection
from django.db.models import Q, Count, Case, When

from stay.models import Booking, Facility, Stay, Review, StayImage
from trip.models import Planner
from misc.models import City
from .serializers import BookingSerailizer, StaySerializer, StayImageSerializer, ReviewSerializer

from migo.utils.customPaginations import CustomPagination
from stay.utils.nearby_google_api import save_nearby_from_google_api
from migo.utils.images_to_dict import modify_input_for_multiple_files

date_format = "%Y-%m-%d"
today = datetime.datetime.now().date()
class CreateStayAPIView(APIView):
    permission_classes = (IsAuthenticated, NotDjangoAdmin, SignUpProcessCompleted, IsHost)
    
    def post(self, request):
        # print("Images Are: ", type(request.FILES.getlist('images')))
        # request.data.update({'user': request.user.id})
        images = dict((request.data).lists()).get('images')
        # images = request.data.get('images')
        print("Images are: ", images)
        # images = request.FILES.getlist('images')
        facilities_string = request.data.get('facilities')

        print('Facilities Are: ', facilities_string)
        print('cost: ', request.data.get('cost'))
        print('title: ', request.data.get('title'))
        facilities = []
        
        if facilities_string:
            try:
                facilities_string = json.loads(facilities_string)
                if not len(facilities_string):
                    return Response({
                        "status": False,
                        "message": "facilities array is required."
                    }, status=400)
                for facility in facilities_string:
                    fa = Facility.objects.filter(title=facility)
                    if not fa.exists():
                        return Response({
                            "status": False,
                            "message": "facilities array must be a proper format"
                        }, status=400)
                    # facilities.append(fa.first().id)
            except Exception as e:
                print(e)
                return Response({
                    "status": False,
                    "message": "facilities array is not property formmated",
                    "field": "facilities"
                }, status=400)
        else:
            return Response({
                "status": False,
                "message": "facilities array is required",
                "field": "facilities"
            }, status=400)


        if images and len(images):
            # request.data.update({"facilities": facilities})
            stay_serializer = StaySerializer(data=request.data, context={ 'request': request})
            stay_serializer.is_valid(raise_exception=True)
            stay_serializer.save()

            print("stay serializer: ", stay_serializer)

            images_arr = []
            for img_name in images:
                modified_data = modify_input_for_multiple_files('stay',stay_serializer.data['id'], img_name)
                print("modified serializer: ", modified_data)
                file_serializer = StayImageSerializer(data=modified_data)
                file_serializer.is_valid(raise_exception=True)
                file_serializer.save()
                print("file serializer: ", modified_data)
                images_arr.append(file_serializer.data)

            save_nearby_from_google_api(stay_serializer.data['id'])
            
            save_facilities(facilities_string, stay_serializer.data['id'])

            stay = Stay.objects.get(id=stay_serializer.data['id'])
            serializer = StaySerializer(stay, context={ 'request': request})

            return Response({
                "status": True,
                "data": serializer.data
            })
        else:
            return Response({
                "status": False,
                "message": "images field is required, upload atleast one image for your property!",
                "field": "images"
            }, status=400)



class UpdateStayAPIView(APIView):
    
    def post(self, request, stay_id):
        status = request.data.get('status')
        if status:
            if status != 'Active' and status != 'InActive':
                return Response({
                    "status": False,
                    "message": "status options are Active and InActive"
                }, status=400)
        try:
            stay = Stay.objects.get(id=stay_id)

            if stay.user != request.user:
                return Response({
                    "status": False,
                    "message": "You Do not have permission!"
                }, status=400)

        except Stay.DoesNotExist:
            return Response({
                "status": False,
                "message": "No Stay Found"
            }, status=400)

        images = dict((request.data).lists()).get('images')
        # images = request.FILES.getlist('images')

        facilities = request.data.get('facilities')
        
        if facilities:
            try:
                facilities = json.loads(facilities)
                save_facilities(facilities, stay.id)
            except Exception as e:
                print(e)
                return Response({
                    "status": False,
                    "message": "facilities array is not property formmated"
                }, status=400)

        stay_serializer = StaySerializer(stay, data=request.data, partial=True)
        stay_serializer.is_valid(raise_exception=True)
        stay_serializer.save()

        print(stay_serializer.data)
        if images:
            images_arr = []
            for img_name in images:
                modified_data = modify_input_for_multiple_files('stay', stay.id, img_name)
                file_serializer = StayImageSerializer(data=modified_data)
                file_serializer.is_valid(raise_exception=True)
                file_serializer.save()
                images_arr.append(file_serializer.data)

        save_nearby_from_google_api(stay_serializer.data['id'])


        serializer = StaySerializer(Stay.objects.get(id=stay.id), context={ 'request': request})
        return Response({
            "status": True,
            "message": "Stay Has been Updated successully!",
            "data": serializer.data
        })

class StayDetailsAPIView(APIView):

    def get(self, request, stay_id):
        try:
            stay = Stay.objects.get(id=stay_id)
        except Stay.DoesNotExist:
            return Response({
                "status": False,
                "message": "No Stay Found!"
            }, status=400)

        serializer = StaySerializer(stay, context={ 'request': request})
        return Response({
            "status": True,
            "data": serializer.data
        })

class StayListingAPIView(APIView, CustomPagination):

    def get(self, request):
        location_latitude = request.query_params.get('latitude', None)
        location_longitude = request.query_params.get('longitude', None)
        city_name = request.query_params.get('city_name', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        guests = request.query_params.get('guests', None)
        stay_type = request.query_params.get('property_type', None)
        price = request.query_params.get('price', None)
        facilities = request.query_params.get('facilities', None)
        print('facilitiies: ', facilities)

        if guests:
            try:
                guests = int(guests)
            except Exception as e:
                print(e)
                return Response({
                    "status": False,
                    "message": "guests should be a Positive Number",
                    "field": "guests"
                })
        else:
            guests = 1

        booking_stays_ids = []
        if start_date and end_date:
            try:
                bookings = Booking.objects.filter(Q(start_date__gte=start_date) & Q(end_date__lte=end_date) & Q(paid=True) & (Q(status='Approved') | Q(status="Pending"))).select_related('stay')
                print('Bookings: ', bookings)
                for booking in bookings:
                    booking_stays_ids.append(booking.stay.id)
            except Exception as e:
                print(e)
                return Response({
                    "status": False,
                    "message": "start_date and end_date should be in property format YYYY-MM-DD",
                    "field": "start_date",
                }, status=400)

        booking_stays_ids_tupple_string = ''

        # Removing trailing ',' in tuple if there's only one element in booking_stays-ids
        if len(booking_stays_ids):
            booking_stays_ids_tupple_string = str(tuple(booking_stays_ids))

            if len(booking_stays_ids) == 1:
                booking_stays_ids_tupple_string = booking_stays_ids_tupple_string[:-2] + booking_stays_ids_tupple_string[-1]

        print('booking List Ids: ', booking_stays_ids)
        print('booking Ids: ', booking_stays_ids_tupple_string)
    
            
        if city_name:
            # if not City.objects.filter(title__icontains=city_name).exists():
            # if not City.objects.filter(title=city_name).exists():
            #     return Response({
            #         "status": False,
            #         "message": "city_name not valid",
            #         "field": "city_name"
            #     })
            if len(booking_stays_ids):
                stays = Stay.objects.filter(Q(location__icontains=city_name) & Q(id__in=booking_stays_ids) & Q(status='Active'))
            else:
                stays = Stay.objects.filter(Q(location__icontains=city_name) & Q(status='Active'))
            print('Stays with city_name: ', stays)
        else:

            if not location_latitude or not location_longitude:
                user = request.user
                if user.location_latitude and user.location_longitude:
                    location_latitude = user.location_latitude
                    location_longitude = user.location_longitude
                else:
                    location = user.interested_location.filter(location_longitude__isnull=False)
                    if location.exists:
                        if location.first().location_latitude:
                            location_latitude = location.first().location_latitude
                            location_longitude = location.first().location_longitude

            try:
                if location_latitude and location_longitude:
                    cursor = connection.cursor()

                    cursor.execute("""SELECT id FROM (
                            SELECT *,
                                (
                                    (
                                        (
                                            acos(
                                                sin(( {0} * pi() / 180))
                                                *
                                                sin(( location_latitude * pi() / 180)) + cos(( {0} * pi() /180 ))
                                                *
                                                cos(( location_latitude * pi() / 180)) * cos((( {1} - location_longitude) * pi()/180)))
                                        ) * 180/pi()
                                    ) * 60 * 1.1515 * 1.609344
                                )
                            as distance FROM stay_stay
                        ) game
                        WHERE status='Active' AND max_guests_allowed >= {2} {3}
                        ORDER BY distance;""".format(location_latitude, location_longitude, guests, 'AND id NOT IN {}'.format(booking_stays_ids_tupple_string) if len(booking_stays_ids) else ''))

                    rows = cursor.fetchall()
                    print('Fetched Rows Are: ', rows)

                    stay_ids = []
                    for row in rows:
                        stay_ids.append(int(row[0]))
                    print('Stay IDs: ', stay_ids)
                    
                    stays = Stay.objects.filter(id__in=stay_ids)
                else:
                    if len(booking_stays_ids):
                        stays = Stay.objects.filter(Q(location__icontains=city_name) & ~Q(id__in=booking_stays_ids) & Q(status='Active'))
                    else:
                        stays = Stay.objects.filter(Q(location__icontains=city_name) & Q(status='Active'))

            except Exception as e:
                print(e)
                return Response({
                    "status": False,
                    "message": "latitude and longitude formats or values are wrong",
                    "field": "latitude"
                }, status=400)
        
        if stay_type:
            stays = stays.filter(stay_type=stay_type)
        
        if price:
            try:
                starting_price, ending_price = price.split('-')
                stays = stays.filter(Q(cost__gte=starting_price), Q(cost__lte=ending_price))
            except Exception as e:
                return Response({
                    "status": False,
                    "message": "price should be NUMBER-NUMBER format",
                    "field": "price"
                })

        if facilities:
            try:
                facilities = json.loads(facilities)
                facilities = list(facilities)
                facilities_ids = []
                try:
                    for i in facilities:
                        facilities_ids.append(Facility.objects.get(title=i).id)
                except Exception as e:
                    print('Exception with facilites: ', e)
                
                print("Facilites Ids are: ", facilities_ids)
                stays = stays.filter(facilities__in=facilities_ids).annotate(num_attr=Count('facilities')).filter(num_attr=len(facilities))
            except Exception as e:
                print(e)
                return Response({
                    "status": False,
                    "message": "facilites should be properly formatted!",
                    "field": "facilites"
                })

        if not city_name:
            stays = stays.filter(~Q(id__in=booking_stays_ids))

            # stays = list(stays)
            # stays.sort(key=lambda stay: stay_ids.index(stay.id))
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(stay_ids)])
            stays = stays.order_by(preserved)
            print('sorted list: ', stays)
        

        data = self.paginate_queryset(stays, request, view=self)
        serializer = StaySerializer(data, many=True)
        return self.get_paginated_response(serializer.data)


class StayListingOfHostAPIView(APIView, CustomPagination):
    permission_classes = (IsAuthenticated, NotDjangoAdmin, SignUpProcessCompleted, IsHost)

    def get(self, request):
        stays = Stay.objects.filter(user=request.user)

        data = self.paginate_queryset(stays, request, view=self)
        serializer = StaySerializer(data, many=True, context={ 'request': request})
        return self.get_paginated_response(serializer.data)



class StayDeleteAPIView(APIView):

    def post(self, request, stay_id):

        try:
            stay = Stay.objects.get(id=stay_id)
        except Stay.DoesNotExist:
            return Response({
                "status": False,
                "message": "No Stay Found!"
            }, status=400)
        
        if stay.user != request.user:
            return Response({
                "status": False,
                "message": "You Do Not Have Permission!"
            }, status=400)


        if Booking.objects.filter(Q(stay=stay) & Q(end_date__gte=today) & Q(paid=True) & (Q(status="Pending") | Q(status="Approved"))).exists():
            if stay.status == 'Active':
                message = "There are stays currently running, you can't delete the stay right now. You can make this stay InActive to prevent further bookings"
                available_status_option = 'inactive'
            else:
                message = "There are stays currently running, you can't delete the stay right now."
                available_status_option = 'active'
            return Response({
                "status": False,
                "message": message,
                "field": "status",
                "available_status_option": available_status_option
            }, status=400)
        
        else:
            stay.delete()
            return Response({
                "status": True,
                "message": "Stay Successfully Deleted"
            }, status=200)


class BookingCreateAPIView(APIView):

    def post(self, request):
        stay_id: int = request.data.get('stay_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        number_of_adults: int = request.data.get('number_of_adults')
        number_of_children: int = request.data.get('number_of_children', 0)
        planner: int = request.data.get('planner')
        extra_mattress: int = request.data.get('extra_mattress')
        # print('Extra Mattress are: ', extra_mattress)

        user = request.user

        try:
            stay = Stay.objects.get(id=stay_id)
            if stay.status == 'InActive':
                return Response({
                    "status": False,
                    "message": "Stay is InActive, You can't book it for now."
                })
        except Stay.DoesNotExist:
            return Response({
                "status": False,
                "message": "stay not found"
            }, status=400)
        
        if planner:
            try:
                planner = Planner.objects.get(id=planner)
            except Exception as e:
                return Response({
                    "status": False,
                    "message": "planner not found"
                }, status=400)
        
        # Number of Days
        _start_date = datetime.datetime.strptime(start_date, date_format)
        _end_date = datetime.datetime.strptime(end_date, date_format)

        if _end_date < _start_date:
            return Response({
                "status": False,
                "message": "start_date should be less than end_date.",
                "field": "dates"
            }, status=400)

        delta = _end_date - _start_date
        print(delta.days)

        try:
            bookings = Booking.objects.filter(Q(stay=stay) & Q(start_date__gte=start_date) & Q(end_date__lte=end_date) & Q(paid=True) & ( Q(status="Approved") | Q(status="Pending"))).select_related('stay')
            print('Bookings: ', bookings)
        except Exception as e:
            print(e)
            return Response({
                "status": False,
                "message": "start_date and end_date should be in property format YYYY-MM-DD",
                "field": "start_date",
            }, status=400)

        if bookings.exists():
            return Response({
                "status": False,
                "message": "Stay is booked for such period of time."
            }, status=400)

        if Booking.objects.filter(Q(user=user) & Q(start_date__gte=start_date) & Q(end_date__lte=end_date) & Q(paid=True) & ( Q(status="Approved") | Q(status="Pending"))).exists():
            return Response({
                "status": False,
                "message": "You have already booked other stay for such period of time."
            }, status=400)
        if not number_of_adults :
            return Response({
                "status": False,
                "message": "number_of_adults field is required"
            }, status=400)
        
        number_of_children = number_of_children if number_of_children else 0
        guests = number_of_adults + number_of_children
        print('Guests are : ', guests)

        if stay.max_guests_allowed < guests:
            return Response({
                "status": False,
                "message": "number_of_adults + number_of_children should be less than or equal to max_guests_allowed"
            }, status=400)


        to_be_paid_price = stay.cost * number_of_adults * delta.days
        # to_be_paid_price = float(to_be_paid_price)

        if extra_mattress:
            if not stay.extra_mattress_available:
                return Response({
                    "status": False,
                    "message": "extra_mattress are not available in this stay.",
                    "field": "extra_mattress"
                }, status=400)
            elif stay.number_of_extra_mattress_available < extra_mattress:
                return Response({
                    "status": False,
                    "message": "extra_mattress availablity exceeds than available in this stay.",
                    "field": "extra_mattress"
                }, status=400)
            to_be_paid_price += stay.price_per_extra_mattress * extra_mattress
        
        try:
            user = request.user
            Booking.objects.filter(user=user, paid=False).delete()
            booking = Booking.objects.create(
                user=user,
                stay=stay,
                start_date=start_date,
                end_date=end_date,
                planner=planner,
                number_of_adults=number_of_adults,
                number_of_children=number_of_children,
                paid=True,
                extra_mattress=extra_mattress if extra_mattress else 0,
                price_of_stay=stay.cost,
                paid_amount=to_be_paid_price,
                commission_at_time_of_booking=stay.commission
            )
            booking.save()

            serializer = BookingSerailizer(booking)

            return Response({
                "status": True,
                "message": "Booking created successfully!",
                "data": serializer.data
            })
        except Exception as e:
            print(e)
            return Response({
                "status": False,
                "message": "Something Went Wrong, Please try again later",
            }, status=400)




class BookingstListingAPIView(APIView, CustomPagination):
    permission_classes = (IsAuthenticated, NotDjangoAdmin, SignUpProcessCompleted, IsHost)

    def get(self, request):
        bookings = Booking.objects.filter(Q(stay__user=request.user, paid=True) & ~Q(status = 'Pending'))
        data = self.paginate_queryset(bookings, request, view=self)
        serializer = BookingSerailizer(data, many=True, context={"request": request, "user_type": "host"})
        return self.get_paginated_response(serializer.data)


class BookingRequestListingAPIView(APIView, CustomPagination):
    permission_classes = (IsAuthenticated, NotDjangoAdmin, SignUpProcessCompleted, IsHost)

    def get(self, request):
        bookings = Booking.objects.filter(stay__user=request.user, paid=True, status="Pending")
        data = self.paginate_queryset(bookings, request, view=self)
        serializer = BookingSerailizer(data, many=True)
        return self.get_paginated_response(serializer.data)

class BookingUserListingAPIView(APIView, CustomPagination):

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user, paid=True)
        data = self.paginate_queryset(bookings, request, view=self)
        serializer = BookingSerailizer(data, many=True, context={"request": request, "user_type": "user"})
        return self.get_paginated_response(serializer.data)

class BookingApproveRejectAPIView(APIView):

    def post(self, request):
        booking_id = request.data.get('booking_id')
        status = request.data.get('status')

        if not status:
            return Response({
                "status": False,
                "message": "status is required!",
                "field": "status"
            }, status=400)
        
        if status != 'approve' and status != 'reject':
            return Response({
                "status": False,
                "message": "status options are 'approve' and 'reject'",
                "field": "status"
            }, status=400)


        if not booking_id:
            return Response({
                "status": False,
                "message": "booking_id is required!",
                "field": "booking_id"
            }, status=400)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({
                "status": False,
                "message": "No Booking Found!",
            }, status=400)
        
        if booking.stay.user != request.user:
            return Response({
                "status": False,
                "message": "Not the right User!",
            }, status=400)
        
        if booking.status != 'Pending':
            return Response({
                "status": False,
                "message": "Booking is already {}".format(booking.status),
            }, status=400)

        elif not booking.paid:
            return Response({
                "status": False,
                "message": "Booking isn't paid or fully processed yet",
            }, status=400)
        
        booking.status = 'Approved' if status == 'approve' else 'Rejected'
        booking.save()

        serializer = BookingSerailizer(booking)

        return Response({
            "status": True,
            "message": "Booking is successfully {}".format(booking.status),
            "data": serializer.data
        })


class BookingCancelAPIView(APIView):

    def post(self, request, booking_id):
        by_host = request.data.get('by_host')

        if not booking_id:
            return Response({
                "status": False,
                "message": "booking_id is required!",
                "field": "booking_id"
            }, status=400)

        try:
            booking = Booking.objects.get(id=booking_id)
            stay = booking.stay
        except Booking.DoesNotExist:
            return Response({
                "status": False,
                "message": "No Booking Found!",
            }, status=400)

        if booking.start_date <= today:
            return Response({
                "status": False,
                "message": "Your stay hasn't completed yet, review after it is",
                "field": "dates"
            }, status=400)
        user = request.user

        if booking.stay.user != user and booking.user != user:
            return Response({
                "status": False,
                "message": "Not the right User!",
            }, status=400)
        
        if booking.status != 'Approved':
            if booking.status == 'Pending' and by_host:
                return Response({
                    "status": False,
                    "message": f"Booking is {booking.status} for now, can't cancel such booking.",
                }, status=400)
        
        if booking.status == 'Cancelled By Host' or booking.status == 'Cancelled By User':
            return Response({
                "status": False,
                "message": "Booking is already Cancelled",
            }, status=400)
            

        elif not booking.paid:
            return Response({
                "status": False,
                "message": "Booking isn't paid or fully processed yet",
            }, status=400)
        
        # if by_host == None:
        #     if booking.stay.user == user:
        #         booking.status = "Cancelled By Host"
        #     elif booking.user == user:
        #         booking.status = "Cancelled By User"

        if by_host == True and booking.event.user == user:
            booking.status = "Cancelled By Host"
        elif by_host == False and booking.user == user:
            booking.status = "Cancelled By User"
        else:
            return Response({
                "status": False,
                "messag": "by_host should match the user"
            })

        booking.save()

        serializer = BookingSerailizer(booking)

        return Response({
            "status": True,
            "message": "Booking is successfully {}".format(booking.status),
            "data": serializer.data
        })


class ReviewCreateAPIView(APIView):

    def post(self, request):
        booking_id: int = request.data.get('booking')
        rating: int = request.data.get('rating')
        text: str = request.data.get('text')

        if not booking_id:
            return Response({
                "status": False,
                "message": "booking is required",
                "field": "booking"
            }, status=400)

        if not rating:
            return Response({
                "status": False,
                "message": "rating is required",
                "field": "rating"
            }, status=400)

        if not text:
            return Response({
                "status": False,
                "message": "text is required",
                "field": "text"
            }, status=400)
        
        try:
            booking = Booking.objects.get(id=booking_id)

            if Review.objects.filter(booking=booking).exists():
                return Response({
                    "status": False,
                    "message": "This Stay has already been reviewed by you."
                })

        except Booking.DoesNotExist:
            return Response({
                "status": False,
                "message": "Booking not found with this booking_id"
            }, status=400)
        
        user = request.user
        if booking.user != user:
            return Response({
                "status": False,
                "message": "Permission Denied, Not Your Booking"
            }, status=400)
        
        if booking.cancellation_date:
            if booking.start_date > booking.cancellation_date:
                return Response({
                    "status": False,
                    "message": "This stay was cancelled",
                    "field": "dates"
                }, status=400)

        elif booking.end_date > today:
            return Response({
                "status": False,
                "message": "Your stay hasn't completed yet, review after it is",
                "field": "dates"
            }, status=400)

        elif booking.start_date > booking.end_date:
            return Response({
                "status": False,
                "message": "Can't review for this booking",
                "field": "dates"
            }, status=400)

        if Review.objects.filter(booking=booking).exists():
            return Response({
                "status": False,
                "message": "Review Already Submitted for this stay/booking."
            }, status=400)
        
        serializer = ReviewSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": True,
            "data": serializer.data,
            "message": "review created successfully!"
        })

class DeleteStayImageAPIView(APIView):

    def post(self, request, image_id):
        try:
            image = StayImage.objects.select_related('stay').get(id=image_id)
        except StayImage.DoesNotExist:
            return Response({
                "status": False,
                "message": "No image found for this image_id"
            }, status=400)
        
        if image.stay.user != request.user:
            return Response({
                "status": False,
                "message": "Permission Denied! You do not have permission to execute this task."
            }, status=400)
        
        all_images_of_stay = StayImage.objects.filter(stay=image.stay)
        if all_images_of_stay.count() > 1:
            image.delete()
        else:
            return Response({
                "status": False,
                "message": "Stay needs atleast one image, that's why you can't delete this one pic."
            }, status=400)

        return Response({
            "status": True,
            "message": "Image deleted successfully!"
        })
