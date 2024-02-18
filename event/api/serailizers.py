from stay.api.serializers import BookingUserSerializer, StaySerializer
from django.db.models.aggregates import Sum
from rest_framework import serializers
from event.models import Event, EventImage, Review, Booking
from core.api.serializers import StayHostSerializer
from django.db.models import Avg, Q


class EventSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    overall_rating = serializers.SerializerMethodField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    delete_option_available = serializers.SerializerMethodField()
    people_interested = serializers.SerializerMethodField()
    people_going = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Event
        exclude = ('created_at', 'updated_at',)
        read_only_fields = ('id', 'members')
        # extra_kwargs = {
        #     'user': {'write_only': True},
        # }

    def get_available_seats(self, event):
        response = Booking.objects.filter(Q(event=event) & Q(paid=True) & (Q(status='Approved') | Q(status='Pending'))).aggregate(Sum('members'))
        return event.seats - (response['members__sum'] or 0)
    
    def get_people_interested(self, event):
        return 0
    
    def get_people_going(self, event):
        response = Booking.objects.filter(Q(event=event) & Q(paid=True) & (Q(status='Approved') | Q(status="Pending"))).aggregate(Sum('members'))
        return response['members__sum'] or 0

    def get_delete_option_available(self, event):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            print('user is: ', user)
        if user and not user.is_anonymous and user == event.user:
            if Booking.objects.filter(Q(paid=True) & (Q(status='Approved') | Q(status='Pending'))).exists():
                return False
            else:
                return True
        else:
            return None

    def get_owner(self, stay):
        serializer = StayHostSerializer(stay.user.profile)
        return serializer.data
    
    def get_images(self, event):
        serializer = EventImageSerializer(event.images.all(), many=True)
        return serializer.data
    
    def get_reviews(self, event):
        rating = Review.objects.filter(booking__event=event)
        serailizer = EventReviewSerailizer(rating, many=True)
        return serailizer.data

    def get_overall_rating(self, event):
        rating = Review.objects.filter(booking__event=event).aggregate(Avg('rating'))
        return rating['rating__avg'] or 0

    
    def validate_commission(self, commission):
        if commission < 5 or commission > 25:
            raise serializers.ValidationError({ "commission": ['commission should be between 5 and 25',]})
        
        return commission



class EventImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventImage
        fields = ('id', 'event', 'image')

class EventReviewSerailizer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        exclude = ('updated_at',)
    
    def get_created_at(self, review):
        return review.created_at.strftime('%d %b %Y, %I:%M %p')
    

class EventBookingSerializer(serializers.ModelSerializer):
    guests = serializers.SerializerMethodField()
    event_details = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_by = serializers.SerializerMethodField()
    number_of_days = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        exclude = ('updated_at',)
    
    def get_number_of_days(self, booking):
        delta = booking.event.end_date - booking.event.start_date
        return delta.days
    
    def get_event_details(self, booking):
        serializer = EventSerializer(booking.event)
        return serializer.data

    def get_created_at(self, booking):
        return booking.created_at.strftime('%d %b %Y, %I:%M %p')
    
    def get_created_by(self, booking):
        serializer = BookingUserSerializer(booking.user)
        return serializer.data

    def get_guests(self, booking):
        return int(
            booking.number_of_adults if booking.number_of_adults else 0 +
            booking.number_of_child if booking.number_of_child else 0 +
            booking.number_of_stag if booking.number_of_stag else 0 +
            booking.number_of_couple if booking.number_of_couple else 0 +
            booking.number_of_eves if booking.number_of_eves else 0
        )