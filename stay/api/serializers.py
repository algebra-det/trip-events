
from account.models import MyUser
from stay.models import NearestHotSpots, Stay, StayImage, Facility, Booking, Review
from core.api.serializers import StayHostSerializer
from django.db.models import Q, Avg

import datetime
from rest_framework import serializers

today = datetime.datetime.today()
today_date = datetime.datetime.now().date()

class ReviewSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_id = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()

    class Meta:
        model = Review
        exclude = ('updated_at',)
    
    def get_created_at(self, review):
        return review.created_at.strftime('%d %b %Y, %I:%M %p')
    
    def get_user_id(self, review):
        return review.booking.user.id

    def get_user_name(self, review):
        return review.booking.user.name
    
    def get_user_image(self, review):
        return review.booking.user.profile.image.url

        
    
class FacilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Facility
        fields = ('title', 'image')

class StaySerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    nearby = serializers.SerializerMethodField()
    facilities = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    delete_option_available = serializers.SerializerMethodField()
    overall_rating = serializers.SerializerMethodField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Stay
        exclude = ('created_at', 'updated_at')
        # read_only_fields = ('id',)
        # extra_kwargs = {
        #     'user': {'write_only': True},
        # }

    def get_overall_rating(self, stay):
        rating = Review.objects.filter(booking__stay=stay).aggregate(Avg('rating'))
        return rating['rating__avg'] or 0
    
    def get_delete_option_available(self, stay):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            print('user is: ', user)
        if user and not user.is_anonymous and user == stay.user:
            if Booking.objects.filter(Q(stay=stay) & Q(end_date__gte=today) &(Q(status="Approved") | Q(status="Pending"))).exists():
                return False
            else:
                return True
        else:
            return None
    
    def get_owner(self, stay):
        serializer = StayHostSerializer(stay.user.profile)
        return serializer.data
    
    def get_images(self, stay):
        serializer = StayImageSerializer(stay.images.all(), many=True)
        return serializer.data

    def get_nearby(self, stay):
        serializer = NearestHotSpotsSerializer(stay.nearby.all(), many=True)
        return serializer.data
    
    def get_facilities(self, stay):
        serializer = FacilitySerializer(stay.facilities.all(), many=True)
        return serializer.data

    def get_reviews(self, stay):
        data = Review.objects.filter(booking__stay=stay)
        serializer = ReviewSerializer(data, many=True)
        return serializer.data

    def validate(self, attrs):
        # if attrs.get('extra_mattress_available') == True:
        if attrs.get('extra_mattress_available'):
            if not attrs.get('price_per_extra_mattress'):
                raise serializers.ValidationError('price_per_extra_mattress is required if extra mattress are available')
            elif not attrs.get('number_of_extra_mattress_available'):
                raise serializers.ValidationError('number_of_extra_mattress_available is required if extra mattress are available')
        else:
            attrs.pop('price_per_extra_mattress', None)
            attrs.pop('number_of_extra_mattress_available', None)

        commission = attrs.get('commission')    
        if not commission:
            raise serializers.ValidationError('commission field is required!')
        
        if int(commission) < 5 or int(commission) > 25:
            raise serializers.ValidationError('commission should be betwen 5 to 25')

        return super().validate(attrs)

class StayImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = StayImage
        fields = ('id', 'stay', 'image')

class NearestHotSpotsSerializer(serializers.ModelSerializer):

    class Meta:
        model = NearestHotSpots
        fields = ('stay', 'title')
    
class BookingUserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ('id', 'name', 'location_name', 'image')
    
    def get_image(self, user):
        return user.profile.image.url

class StayDetailsForBookingSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Stay
        fields = ('id', 'title', 'images', 'owner')

    def get_images(self, stay):
        serializer = StayImageSerializer(stay.images.all(), many=True)
        return serializer.data

    def get_owner(self, stay):
        serializer = StayHostSerializer(stay.user.profile)
        return serializer.data
    
class BookingSerailizer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    guests = serializers.SerializerMethodField()
    stay_location_name = serializers.SerializerMethodField()
    stay_details = serializers.SerializerMethodField()
    can_be_cancelled = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        exclude = ('created_at', 'updated_at')
    
    def get_stay_details(self, booking):
        serializer = StayDetailsForBookingSerializer(booking.stay)
        return serializer.data
    
    def get_created_by(self, booking):
        serializer = BookingUserSerializer(booking.user)
        return serializer.data

    def get_guests(self, booking):
        return int(booking.number_of_adults + booking.number_of_children)

    def get_stay_location_name(self, booking):
        return str(booking.stay.location)
    
    def get_can_be_cancelled(self, booking):
        if booking.start_date > today_date:
            user = None
            request = self.context.get("request")
            user_type = self.context.get("user_type")
            print('User Type is: ', user_type)
            if request and hasattr(request, "user"):
                user = request.user
                if user and not user.is_anonymous and user_type:
                    if user_type == 'user':
                        print('user here is: ', user_type)
                        if booking.status == 'Pending' or booking.status== 'Approved':
                            print('Its True')
                            return True
                        else:
                            return False
                    elif user_type == 'host':
                        if booking.status== 'Approved':
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False



class CreateBookingSerailizer(serializers.ModelSerializer):
    stay_id = serializers.CharField()

    class Meta:
        model = Booking
        fields = '__all__'
        # read_only_fields = ('id','price_of_stay', 'paid_amount', 'start_date', 'end_date', 'status', 'paid')