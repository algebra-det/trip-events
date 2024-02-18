from trip.models import Planner
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated
from migo.utils.customPermissionClass import NotDjangoAdmin, SignUpProcessCompleted, IsHost
from migo.utils.images_to_dict import modify_input_for_multiple_files
from migo.utils.customPaginations import CustomPagination
from django.db.models import Q, Case, When

from .serailizers import EventSerializer, EventImageSerializer, EventBookingSerializer
from event.models import Event, Booking, EventImage, Review
class EventCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, NotDjangoAdmin, SignUpProcessCompleted, IsHost)

    def post(self, request):
        images = dict((request.data).lists()).get('images')
        seats: int = request.data.get('seats')
        adult_entry_cost: int = request.data.get('adult_entry_cost')
        child_entry_cost: int = request.data.get('child_entry_cost')
        stag_entry_cost: int = request.data.get('stag_entry_cost')
        couple_entry_cost: int = request.data.get('couple_entry_cost')
        eves_entry_cost: int = request.data.get('eves_entry_cost')

        if not seats or seats == "0":
            return Response({
                "status": False,
                "message": "seats field is required and must be number and greater than zero",
                "field": "seats"
            }, status=400)
        
        if not adult_entry_cost or adult_entry_cost == '0':
            if not child_entry_cost or child_entry_cost == '0':
                if not stag_entry_cost or stag_entry_cost == '0':
                    if not couple_entry_cost or couple_entry_cost == '0':
                        if not eves_entry_cost or eves_entry_cost == '0':
                            return Response({
                                "status": False,
                                "message": "Please set price of atleast one type of entry."
                            }, status=400)
    
        if images and len(images):
            # request.data.update({'user': request.user.id})
            event_serializer = EventSerializer(data=request.data, context={'request': request})
            event_serializer.is_valid(raise_exception=True)
            event_serializer.save()

            images_arr = []
            for img_name in images:
                modified_data = modify_input_for_multiple_files('event',event_serializer.data['id'], img_name)
                file_serializer = EventImageSerializer(data=modified_data)
                file_serializer.is_valid(raise_exception=True)
                file_serializer.save()
                images_arr.append(file_serializer.data)

            stay = Event.objects.get(id=event_serializer.data['id'])
            serializer = EventSerializer(stay, context={'request': request})

            return Response({
                "status": True,
                "message": "Event created Successfully.",
                "data": serializer.data
            })
        else:
            return Response({
                "status": False,
                "message": "images field is required, upload atleast one image for your property!",
                "field": "images"
            }, status=400)

class EventUpdateAPIView(APIView):

    def post(self, request, event_id):

        status = request.data.get('status')
        if status:
            if status != 'Active' and status != 'InActive':
                return Response({
                    "status": False,
                    "message": "status options are Active and InActive"
                }, status=400)

        user = request.user
        images = request.data.get('images')
        adult_entry_cost: int = request.data.get('adult_entry_cost')
        child_entry_cost: int = request.data.get('child_entry_cost')
        stag_entry_cost: int = request.data.get('stag_entry_cost')
        couple_entry_cost: int = request.data.get('couple_entry_cost')
        eves_entry_cost: int = request.data.get('eves_entry_cost')

        print('adult entry cost: ', type(adult_entry_cost), adult_entry_cost)

        if adult_entry_cost and adult_entry_cost == '0':
            return Response({
                "status": False,
                "message": "adult_entry_cost should be more than 1"
            }, status=400)
        if child_entry_cost and child_entry_cost == '0':
            return Response({
                "status": False,
                "message": "child_entry_cost should be more than 1"
            }, status=400)
        if stag_entry_cost and stag_entry_cost == '0':
            return Response({
                "status": False,
                "message": "stag_entry_cost should be more than 1"
            }, status=400)
        if couple_entry_cost and couple_entry_cost == '0':
            return Response({
                "status": False,
                "message": "couple_entry_cost should be more than 1"
            }, status=400)
        if eves_entry_cost and eves_entry_cost == '0':
            return Response({
                "status": False,
                "message": "eves_entry_cost should be more than 1."
            }, status=400)
    
        if images:
            images = dict((request.data).lists()).get('images')
        seats: int = request.data.get('seats')

        if seats and seats == "0":
            return Response({
                "status": False,
                "message": "seats field is required and must be number and greater than zero",
                "field": "seats"
            }, status=400)

        try:
            event = Event.objects.get(id=event_id)
            if event.user != user:
                return Response({
                    "status": False,
                    "message": "Do not have permission!"
                }, status=400)

        except Event.DoesNotExist:
            return Response({
                "status": False,
                "message": "No event found with such id"
            }, status=400)

        event_serializer = EventSerializer(event, data=request.data, partial=True, context={'request': request})
        event_serializer.is_valid(raise_exception=True)
        event_serializer.save()

        if images and len(images):

            images_arr = []
            for img_name in images:
                modified_data = modify_input_for_multiple_files('event', event_id, img_name)
                file_serializer = EventImageSerializer(data=modified_data)
                file_serializer.is_valid(raise_exception=True)
                file_serializer.save()
                images_arr.append(file_serializer.data)

            stay = Event.objects.get(id=event_id)
            serializer = EventSerializer(stay, context={'request': request})

            return Response({
                "status": True,
                "message": "Event updated Successfully.",
                "data": serializer.data
            })
        else:
            return Response({
                "status": True,
                "message": "event has been updated Successfully.",
                "data": event_serializer.data
            })

class EventDetailsAPIView(APIView):

    def get(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({
                "status": False,
                "message": "No Event Found with this ID."
            }, status=400)
        
        serializer = EventSerializer(event)
        return Response({
            "status": True,
            "data": serializer.data
        })

class EventDeleteAPIView(APIView):

    def post(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({
                "status": False,
                "message": "No Event Found with this ID."
            }, status=400)
        
        bookings = Booking.objects.filter(Q(event=event) & Q(status='Pending') & Q(status="Approved"))
        if bookings.exists():
            return Response({
                "status": False,
                "message": "This event has bookings, cancel them in order to delete this event. You can inActive it to prevent any further bookings."
            }, status=400)
        
        event.delete()
        return Response({
            "status": True,
            "message": "Event has been successfully deleted."
        })

class EventListingOfHostAPIView(APIView, CustomPagination):
    permission_classes = (IsAuthenticated, NotDjangoAdmin, SignUpProcessCompleted, IsHost)

    def get(self, request):
        events = Event.objects.filter(user=request.user)

        data = self.paginate_queryset(events, request, view=self)
        serializer = EventSerializer(data, many=True, context={ 'request': request})
        return self.get_paginated_response(serializer.data)


class EventListingAPIView(APIView, CustomPagination):

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        location = request.query_params.get('location')
        number_of_people: int = request.query_params.get('number_of_people')
        event_type = request.query_params.get('type')
        rating = request.query_params.get('rating')
        price = request.query_params.get('price')

        adults = request.data.get('adults')
        child = request.data.get('child')
        stag = request.data.get('stag')
        eves = request.data.get('eves')
        couple = request.data.get('couple')


        if number_of_people:
            number_of_people = int(number_of_people)

        user = request.user

        # Getting users all bookings to filter out the events he/she has already booked
        bookings = Booking.objects.filter(user=user).select_related('event')
        events_ids = []
        for booking in bookings:
            events_ids.append(booking.event.id)
        events = Event.objects.filter(Q(status='Active') & ~Q(id__in=events_ids))

        if start_date and end_date:
            try:
                events = events.filter(Q(start_date__gte=start_date) & Q(end_date__lte=end_date))
                print('Such Events Are: ', events)
            except Exception as e:
                print(e)
                return Response({
                    "status": False,
                    "message": "start_date and end_date must be in YYYY-MM-DD Format."
                }, status=400)
        
        if location:
            events = events.filter(location__icontains=location)
        
        if event_type:
            events = events.filter(event_type=event_type)
        
        if rating == 'high':
            event_ids = [ event.id for event in events ]
            print('Event IDs from above Filters: ', event_ids)
            reviews = Review.objects.filter(booking__event__id__in=event_ids).select_related('booking').order_by('-rating')
            top_rating_order_of_events = [review.booking.event.id for review in reviews]
            print('Top Rating Order Of Events: ', top_rating_order_of_events)

            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(top_rating_order_of_events)])
            events = events.order_by(preserved)
            print('Events sorted: ', events)
        
        if price:
            if price == 'high':
                events = events.order_by(
                    '-adult_entry_cost',
                    '-child_entry_cost',
                    '-stag_entry_cost',
                    '-eves_entry_cost',
                    '-couple_entry_cost'
                )
            elif price == 'low':
                events = events.order_by(
                    'adult_entry_cost',
                    'child_entry_cost',
                    'stag_entry_cost',
                    'eves_entry_cost',
                    'couple_entry_cost'
                )

            else:
                if not adults and not child and not stag and not eves and not couple:
                    return Response({
                        "status": False,
                        "message": "Please select atleast one of the types of entries in order to filter according to price."
                    }, status=400)
            
                if adults:
                    events = events.order_by('adult_entry_cost')
                if child:
                    events = events.order_by('child_entry_cost')
                if stag:
                    events = events.order_by('stag_entry_cost')
                if eves:
                    events = events.order_by('eves_entry_cost')
                if couple:
                    events = events.order_by('couple_entry_cost')
        
        if adults:
            events = events.filter(adult_entry_cost__gt=0)
        if child:
            events = events.filter(child_entry_cost__gt=0)
        if stag:
            print('Filtering for Stag:')
            events = events.filter(stag_entry_cost__gt=0)
        if eves:
            events = events.filter(eves_entry_cost__gt=0)
        if couple:
            events = events.filter(couple_entry_cost__gt=0)

        if number_of_people and events.exists():
            for event in events:
                print("Event available seats: ", type(event.available_seats) , event.available_seats)
            print('Number of People: ', type(number_of_people), number_of_people)
            events = [event for event in events if int(event.available_seats) >= number_of_people]
        
        data = self.paginate_queryset(events, request, view=self)
        serializer = EventSerializer(data, many=True)
        return self.get_paginated_response(serializer.data)

class EventBookingCreateAPIView(APIView):

    def post(self, request):
        number_of_adults: int = request.data.get('number_of_adults')
        number_of_child: int= request.data.get('number_of_child')
        number_of_stag: int = request.data.get('number_of_stag')
        number_of_eves: int = request.data.get('number_of_eves')
        number_of_couple: int = request.data.get('number_of_couple')

        event_id: int = request.data.get('event_id')
        planner_id: int = request.data.get('planner')

        planner = None
        if planner_id:
            try:
                planner = Planner.objects.get(id=planner_id)
            except Planner.DoesNotExist:
                return Response({
                    "status": False,
                    "message": "planner not found with this planner_id"
                }, status=400)
        
        if not event_id:
            return Response({
                "status": False,
                "message": "event_id is required."
            }, status=400)


        user = request.user
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({
                "status": False,
                "message": "No Event Found for such ID"
            }, status=400)
        
        if Booking.objects.filter(Q(user=user) & Q(event__start_date__gte=event.start_date) & Q(event__end_date__lte=event.end_date) & Q(paid=True) & (Q(status="Pending") | Q(status="Approved"))).exists():
            return Response({
                "status": False,
                "message": "You have already booked an Event which is overlapping with this event's Timings."
            }, status=400)
        
        if not number_of_adults or number_of_adults == '0':
            if not number_of_child or number_of_child == '0':
                if not number_of_stag or number_of_stag == '0':
                    if not number_of_eves or number_of_eves == '0':
                        if not number_of_couple or number_of_couple == '0':
                            return Response({
                                "status": False,
                                "message": "Please select atleast one of the types of entries."
                            }, status=400)
        
        if number_of_adults and not event.adult_entry_cost:
            return Response({
                "status": False,
                "message": "no entry or different price of adult."
            }, status=400)
        if number_of_child and not event.child_entry_cost:
            return Response({
                "status": False,
                "message": "no entry or different price of child."
            }, status=400)
        if number_of_couple and not event.couple_entry_cost:
            return Response({
                "status": False,
                "message": "no entry or different price of couple."
            }, status=400)
        if number_of_stag and not event.stag_entry_cost:
            return Response({
                "status": False,
                "message": "no entry or different price of stag."
            }, status=400)
        if number_of_eves and not event.eves_entry_cost:
            return Response({
                "status": False,
                "message": "no entry or different price of eves."
            }, status=400)
        

        members = int(
            number_of_adults if number_of_adults else 0 +
            number_of_child if number_of_child else 0 +
            number_of_couple if number_of_couple else 0 +
            number_of_eves if number_of_eves else 0 +
            number_of_stag if number_of_stag else 0
        )

        if members > event.available_seats:
            return Response({
                "status": False,
                "message": "Total Number of members exceed events available seats"
            }, status=400)
        

        booking = Booking()
        total_price = 0
        if number_of_adults:
            total_price += number_of_adults * event.adult_entry_cost
            booking.number_of_adults = number_of_adults

        if number_of_child:
            total_price += number_of_child * event.child_entry_cost
            booking.number_of_child = number_of_child

        if number_of_stag:
            total_price += number_of_stag * event.stag_entry_cost
            booking.number_of_stag = number_of_stag

        if number_of_couple:
            total_price += number_of_couple * event.couple_entry_cost
            booking.number_of_couple = number_of_couple

        if number_of_eves:
            total_price += number_of_eves * event.eves_entry_cost
            booking.number_of_eves = number_of_eves
        
        booking.paid_amount = total_price
        booking.event = event
        booking.user = user
        booking.paid = True
        booking.adult_entry_cost = event.adult_entry_cost
        booking.child_entry_cost = event.child_entry_cost
        booking.stag_entry_cost = event.stag_entry_cost
        booking.couple_entry_cost = event.couple_entry_cost
        booking.eves_entry_cost = event.eves_entry_cost
        booking.commission_at_time_of_booking=event.commission
        booking.planner = planner

        try:
            Booking.objects.filter(user=user, paid=False).delete()
            booking.save()
        except Exception as e:
            print(e)
            return Response({
                "status": False,
                "message": "Something went wrong while processing your booking request. Please try again lalter."
            }, status=400)
        
        serializer = EventBookingSerializer(booking)
    
        return Response({
            "status": True,
            "data": serializer.data
        })

        
class EventBookingRequestsAPIView(APIView, CustomPagination):
    permission_classes = (IsAuthenticated, NotDjangoAdmin, SignUpProcessCompleted, IsHost)

    def get(self, request):
        user = request.user
        bookings = Booking.objects.filter(event__user=user, paid=True, status="Pending")
        
        data = self.paginate_queryset(bookings, request, view=self)
        serializer = EventBookingSerializer(data, many=True)
        return self.get_paginated_response(serializer.data)


class EventBookingUserListingAPIView(APIView, CustomPagination):

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user, paid=True)
        data = self.paginate_queryset(bookings, request, view=self)
        serializer = EventBookingSerializer(data, many=True)
        return self.get_paginated_response(serializer.data)


class EventBookingApproveRejectAPIView(APIView):

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
        
        if booking.event.user != request.user:
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

        serializer = EventBookingSerializer(booking)

        return Response({
            "status": True,
            "message": "Booking is successfully {}".format(booking.status),
            "data": serializer.data
        })

class EventBookingstListingAPIView(APIView, CustomPagination):
    permission_classes = (IsAuthenticated, NotDjangoAdmin, SignUpProcessCompleted, IsHost)

    def get(self, request):
        bookings = Booking.objects.filter(Q(event__user=request.user, paid=True) & ~Q(status = 'Pending'))
        data = self.paginate_queryset(bookings, request, view=self)
        serializer = EventBookingSerializer(data, many=True)
        return self.get_paginated_response(serializer.data)


class EventBookingCancelAPIView(APIView):

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
            event = booking.event
        except Booking.DoesNotExist:
            return Response({
                "status": False,
                "message": "No Booking Found!",
            }, status=400)

        user = request.user

        if event.user != user and booking.user != user:
            return Response({
                "status": False,
                "message": "Not the right User!",
            }, status=400)
        
        if booking.status != 'Approved':
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
        #     if event.user == user:
        #         booking.status = "Cancelled By Host"
        #     elif booking.user == user:
        #         booking.status = "Cancelled By User"

        if by_host == True and event.user == user:
            booking.status = "Cancelled By Host"
        elif by_host == False and booking.user == user:
            booking.status = "Cancelled By User"
        else:
            return Response({
                "status": False,
                "messag": "by_host should match the user"
            })

        booking.save()

        serializer = EventBookingSerializer(booking)

        return Response({
            "status": True,
            "message": "Booking is successfully {}".format(booking.status),
            "data": serializer.data
        })


class DeleteEventImageAPIView(APIView):

    def post(self, request, image_id):
        try:
            image = EventImage.objects.select_related('event').get(id=image_id)
        except EventImage.DoesNotExist:
            return Response({
                "status": False,
                "message": "No image found for this image_id"
            }, status=400)
        
        if image.event.user != request.user:
            return Response({
                "status": False,
                "message": "Permission Denied! You do not have permission to execute this task."
            }, status=400)
        
        all_images_of_event = EventImage.objects.filter(event=image.event)
        if all_images_of_event.count() > 1:
            image.delete()
        else:
            return Response({
                "status": False,
                "message": "Event needs atleast one image, that's why you can't delete this one pic."
            }, status=400)

        return Response({
            "status": True,
            "message": "Image deleted successfully!"
        })
