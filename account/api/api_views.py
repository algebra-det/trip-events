from django.contrib import auth
from rest_framework import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
import rest_framework_simplejwt
from rest_framework_simplejwt.views import TokenRefreshView

from account.models import MyUser, Code, TempToken
from account.api.utils import get_code, sending_email, sending_code
from migo.utils.misc import blacklist_token
import datetime

from core.models import BankDetails, Profile
from misc.models import TravelType, TripInterest, City
from core.api.serializers import BankDetailsSetSerializer, ProfileBioSetSerializer
from .serializers import CustomTokenVerifySerializer, ProfileSetSerializer, CustomTokenRefreshSerializer

from account.api.serializers import LoginSerializer, RegisterSerializer, ChangePasswordSerializer

from rest_framework_simplejwt.tokens import RefreshToken

class TokenRefreshAPIView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

class TokenVerifyAPIView(TokenRefreshView):
    serializer_class = CustomTokenVerifySerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def check_expiration_code(time):
    code_created_time = time
    time_elapsed = datetime.datetime.now().timestamp() - code_created_time.timestamp()
    if time_elapsed > 1800:
        return False
    return True

def get_random_code():
    random_code = get_code()
    exists = True
    if exists:
        if Code.objects.filter(confirmation_code=random_code).exists():
            random_code = get_code()
        else:
            exists = False
    return random_code

class CurrentUserView(APIView):

    def get(self, request):
        user = request.user
        if user.is_verified and user.sign_up_steps == 'Wander List Set':
            token = get_tokens_for_user(user)

            userDict = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'verified_account': user.verified_account,
                "user_type": 'host' if user.is_host else 'traveller',
            }

            return Response({
                "status": True,
                "user": userDict,
                "token": token['access'],
                "refresh": token['refresh']
            }, status=200)
        else:
            return Response({"status": False, "message": "User is not authorized!"}, status=400)
        


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):

        phone = request.data.get('phone')
        if not phone:
            return Response({
                'status': False,
                'message': 'phone field is required',
                'field': 'phone'
            }, status=400)
        
        if (len(phone) < 10 or len(phone) > 10):
            return Response({
                'status': False,
                'phone': phone,
                'message': 'phone number not valid',
                'field': 'phone'
            }, status=400)

        try:
            phone = int(phone)
            phone = str(phone)
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'phone': phone,
                'message': 'phone number not valid',
                'field': 'phone'
            }, status=400)

        old_users = MyUser.objects.filter(phone=phone)
        if old_users.exists():
            old_user = old_users.first()

            if old_user.sign_up_steps == 'OTP Sent' or old_user.sign_up_steps == 'OTP Verified':
                random_code = get_code()
                Code.objects.filter(user=old_user).delete()
                Code.objects.create(user=old_user, confirmation_code=random_code, usage='Register')
                TempToken.objects.filter(user=old_user).delete()
                request_response = sending_code(random_code, old_user.email, phone, 'register')
                if request_response:
                    return Response({
                        'status': True,
                        'phone': phone,
                        'message': 'Check Your SMS For Verification Code!'
                    }, status=201)
                else:
                    return Response({
                        "status": False,
                        "message": "Something Went Wrong while sending OTP to {}, Please Try Again Later!".format(phone)
                        }, status=400)



            else:
                return Response({
                    'status': False,
                    'message': 'This Phone Number already exists, Login with this phone number.',
                    "goTo": "login"
                }, status=400)

        else:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            profile = Profile.objects.create(user=user)
            profile.save()

            bank_details = BankDetails.objects.create(user=user)
            bank_details.save()

            random_code = get_random_code()
            Code.objects.create(user=user, confirmation_code=random_code, usage='Register')

            request_response = sending_code(random_code, user.email, phone, 'register')

            return Response({
                'status': True,
                'phone': phone,
                'message': 'Check Your SMS For Verification Code!'
            }, status=201)
            # if request_response:
            #     return Response({
            #         'status': True,
            #         'phone': phone,
            #         'message': 'Check Your SMS For Verification Code!'
            #     }, status=201)
            # else:
            #     return Response({"status": False, "message": "Something Went Wrong while sending OTP to {}, Please Try Again Later!".format(phone)})


class OTPVerifyView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        otp = request.data.get('otp', None)
        phone = request.data.get('phone', None)
        if not otp or not phone:
            return Response({
                'status': False,
                'message': 'OTP and Phone is required',
                'field': 'opt and phone'
            }, status=400)

        try:
            code = Code.objects.get(confirmation_code=otp)
            user = code.user
        except Code.DoesNotExist:
            return Response({
                'status': False,
                'message': 'Not Valid Code or Expired, Request a New One',
                'field': 'otp'
            }, status=400)

        if code.user.phone != phone:
            print(code, user.phone, phone)
            return Response({
                'status': False,
                'message': 'Code Expired or Incorrect',
                'field': 'code'
            }, status=400)
        TempToken.objects.filter(user=user).delete()
        temp_code = TempToken(user=user)
        temp_code.save()

        user.sign_up_steps = 'OTP Verified'
        user.save()
        code.delete()

        return Response({
            'status': True,
            'tempToken': temp_code.token,
            'message': 'Successfully Verified, Go To Password Screen'
        })

class SetPasswordView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        new_password = request.data.get('new_password', None)
        confirm_password = request.data.get('confirm_password', None)
        tempToken = request.data.get('tempToken', None)

        if not new_password:
            return Response({
                'status': False,
                'message': 'new_password field is required',
                'field': 'new_password'
            }, status=400)
        elif not confirm_password:
            return Response({
                'status': False,
                'message': 'confirm_password field is required',
                'field': 'confirm_password'
            }, status=400)
        elif not tempToken:
            return Response({
                'status': False,
                'message': 'tempToken is required'
            }, status=400)
        
        elif new_password!=confirm_password:
            return Response({
                'status': False,
                'message': 'Passwords do not match',
                'field': 'password'
            }, status=400)
            

        elif len(new_password) < 8:
            return Response({
                'status': False,
                'message': 'Password must be atleast 8 characters'
            }, status=400)

        try:
            temp_token = TempToken.objects.get(token=tempToken)
        except TempToken.DoesNotExist:
            return Response({
                'status': False,
                'message': 'No Token Found or Token Expired',
                'field': 'tempToken'
            })

        if not temp_token:
            return Response({
                'status': False,
                'goTo': 'signUp',
                'message': 'signUp First'
            }, status=400)

        elif temp_token.user.sign_up_steps != 'OTP Verified':
            return Response({
                'status': False,
                'goTo': 'signUp',
                'message': 'Sign Up again'
            }, status=400)
        
        temp_token.user.set_password(new_password)
        temp_token.user.sign_up_steps = 'Password Set'
        temp_token.user.save()

        return Response({
            'status': True,
            'message': 'Successfully added, Set Email',
            'tempToken': tempToken
        })

import re
class SetEmail(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email', None)
        tempToken = request.data.get('tempToken', None)

        if not email or not tempToken:
            return Response({
                'status': False,
                'message': 'email and tempToken is required',
                'field': 'email and tempToken'
            }, status=400)

        try:
            temp_token = TempToken.objects.get(token=tempToken)
            user = temp_token.user
        except TempToken.DoesNotExist:
            return Response({
                'status': False,
                'message': 'No Token Found or Token Expired',
                'field': 'tempToken'
            })

        if not temp_token:
            return Response({
                'status': False,
                'goTo': 'signUp',
                'message': 'signUp First'
            }, status=400)

        elif user.sign_up_steps == 'OTP Sent' or user.sign_up_steps == 'OTP Verified':
            return Response({
                'status': False,
                'goTo': 'signUp',
                'message': 'Sign Up again'
            }, status=400)

        elif user.sign_up_steps != 'Password Set':
            return Response({
                'status': False,
                'goTo': 'login',
                'message': 'login to complete your signUp process'
            }, status=400)

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        if MyUser.objects.filter(email=email).exists():
            return Response({
                "status": False,
                "message": "This Email is already being Used",
                "field": "email"
            }, status=400)

        if(re.fullmatch(regex, email)):
            user.email = email
            user.sign_up_steps = 'Email Set'
            user.save()

            return Response({
                'status': True,
                'message': 'Successfully added, Set Profile',
                'tempToken': tempToken,
                'email': temp_token.user.email
            })

        else:
            return Response({
                'status': False,
                'message': 'Email Not Valid',
                'field': 'email'
            }, status=400)

class SetProfileView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        tempToken = request.query_params.get('tempToken', None)

        try:
            temp_token = TempToken.objects.get(token=tempToken)
            user = temp_token.user
        except TempToken.DoesNotExist:
            return Response({
                'status': False,
                'message': 'No Token Found or Token Expired'
            }, status=400)
        

        bank_account = BankDetails.objects.get(user=user)
        profile_set_serializer = ProfileSetSerializer(user)
        profile_set_serializer = ProfileSetSerializer(user)
        profile_bio_set_serializer = ProfileBioSetSerializer(user.profile)
        bank_details_set_serializer = BankDetailsSetSerializer(bank_account)
        response = {}
        response.update(profile_set_serializer.data)
        response.update(profile_bio_set_serializer.data)
        response.update(bank_details_set_serializer.data)
        return Response({
            "status": True,
            "data": response
        })



    def post(self, request):
        tempToken = request.data.get('tempToken', None)
        email = request.data.get('email', None)

        try:
            temp_token = TempToken.objects.get(token=tempToken)
            user = temp_token.user
        except TempToken.DoesNotExist:
            return Response({
                'status': False,
                'message': 'No Token Found or Token Expired'
            }, status=400)

        
        if email:
            emailed_user = MyUser.objects.filter(email=email)
            if emailed_user.exists():
                if user != emailed_user.first():
                    return Response({
                        "status": False,
                        "message": "This email is already registered."
                    }, status=400)

        if user.sign_up_steps == 'Profile Set':
            return Response({
                "status": False,
                "message": "Profile Already Set, Login"
            }, status=400)


        elif user.sign_up_steps != 'Email Set' and user.sign_up_steps != 'Wander List Set':
            return Response({
                'status': False,
                'goTo': 'login',
                'message': 'Login Again'
            }, status=400)
        
        try:
            bank_account = BankDetails.objects.get(user=user)
        except BankDetails.DoesNotExist:
            return Response({
                'status': False,
                'message': "No User/Bank Details found"
            })

        profile_set_serializer = ProfileSetSerializer(user, data=request.data)
        profile_bio_set_serializer = ProfileBioSetSerializer(user.profile, data=request.data)
        bank_details_set_serializer = BankDetailsSetSerializer(bank_account, data=request.data)

        profile_set_serializer.is_valid(raise_exception=True)
        profile_bio_set_serializer.is_valid(raise_exception=True)
        bank_details_set_serializer.is_valid(raise_exception=True)

        profile_set_serializer.save()
        profile_bio_set_serializer.save()
        bank_details_set_serializer.save()

        user.sign_up_steps = "Profile Set"
        user.save()

        return Response({
            'status': True,
            'message': 'Successfully added, Set Trip Interest',
            'tempToken': tempToken
        }, status=200)

class UpdateProfileView(APIView):

    def get(self, request):
        user = request.user

        bank_account = BankDetails.objects.get(user=user)
        profile_set_serializer = ProfileSetSerializer(user)
        profile_set_serializer = ProfileSetSerializer(user)
        profile_bio_set_serializer = ProfileBioSetSerializer(user.profile)
        bank_details_set_serializer = BankDetailsSetSerializer(bank_account)

        response = {}
        response.update(profile_set_serializer.data)
        response.update(profile_bio_set_serializer.data)
        response.update(bank_details_set_serializer.data)
        return Response({
            "status": True,
            "data": response
        })



    def post(self, request):
        email = request.data.get('email', None)
        
        user = request.user

        if email:
            emailed_user = MyUser.objects.filter(email=email)
            if emailed_user.exists():
                if user != emailed_user.first():
                    return Response({
                        "status": False,
                        "message": "This email is already registered."
                    }, status=400)

        if user.sign_up_steps == 'Profile Set':
            return Response({
                "status": False,
                "message": "Profile Already Set, Login"
            }, status=400)


        bank_account, created = BankDetails.objects.get_or_create(user=user)

        profile_set_serializer = ProfileSetSerializer(user, data=request.data, partial=True)
        profile_bio_set_serializer = ProfileBioSetSerializer(user.profile, data=request.data, partial=True)
        bank_details_set_serializer = BankDetailsSetSerializer(bank_account, data=request.data, partial=True)

        profile_set_serializer.is_valid(raise_exception=True)
        profile_bio_set_serializer.is_valid(raise_exception=True)
        bank_details_set_serializer.is_valid(raise_exception=True)

        profile_set_serializer.save()
        profile_bio_set_serializer.save()
        bank_details_set_serializer.save()

        response = {}
        response.update(profile_set_serializer.data)
        response.update(profile_bio_set_serializer.data)
        response.update(bank_details_set_serializer.data)
        return Response({
            "status": True,
            "data": response
        }, status=200)

import json
class SetTravelTypeView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        travel_type_array = request.data.get('travelTypes', None)
        tempToken = request.data.get('tempToken', None)

        try:
            temp_token = TempToken.objects.get(token=tempToken)
            user = temp_token.user
        except TempToken.DoesNotExist:
            return Response({
                'status': False,
                'message': 'No Token Found or Token Expired',
                'field': 'tempToken'
            }, status=400)

        if not temp_token or not travel_type_array:
            return Response({
                'status': False,
                'message': 'tempToken and travelTypes is required',
                'field': 'tempToken and travelTypes'
            }, status=400)

        elif user.sign_up_steps == 'Travel Type Set':
            return Response({
                'status': False,
                'goTo': 'tripInterest',
                'message': 'Travel Type Already Set, Set Trip Interests'
            }, status=400)

        elif user.sign_up_steps != 'Profile Set':
            return Response({
                'status': False,
                'goTo': 'login',
                'message': 'Login Again'
            }, status=400)
        
        try:
            travel_type_array = json.loads(travel_type_array)
            travel_type_array = list(travel_type_array)

            if not len(travel_type_array):
                return Response({
                    'status': False,
                    'message': 'travelTypeArray can not be empty',
                    'field': 'travelTypes'
                }, status=400)

            for i in travel_type_array:
                if travel_type := TravelType.objects.filter(id=i):
                    if travel_type.first() not in user.travel_type.all():
                        user.travel_type.add(travel_type.first())
            
            if not user.travel_type.all().count():
                return Response({
                    "status": False,
                    "message": "traveTypeArray should be from the list."
                }, status=400)

            user.sign_up_steps = 'Travel Type Set'
            user.save()

            return Response({
                'status': True,
                'message': 'Successfully added, Set Trip Interest',
                'tempToken': tempToken
            })
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': 'travelTypeArray is not properly Formatted',
                'field': 'travelTypes'
            }, status=400)
            

class SetTripInterestsView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        trip_interests_array = request.data.get('tripInterests', None)
        tempToken = request.data.get('tempToken', None)

        try:
            temp_token = TempToken.objects.get(token=tempToken)
            user = temp_token.user
        except TempToken.DoesNotExist:
            return Response({
                'status': False,
                'message': 'No Token Found or Token Expired',
                'field': 'tempToken'
            }, status=400)

        if not temp_token or not trip_interests_array:
            return Response({
                'status': False,
                'message': 'tempToken and tripInterests is required',
                'field': 'tempToken and tripInterests'
            }, status=400)

        elif user.sign_up_steps == 'Trip Interest Set':
            return Response({
                'status': False,
                'goTo': 'tripInterest',
                'message': 'Trip Interests Already Set, Set Wander List'
            }, status=400)

        elif user.sign_up_steps != 'Travel Type Set':
            return Response({
                'status': False,
                'goTo': 'login',
                'message': 'Login Again'
            }, status=400)
        
        try:
            trip_interests_array = json.loads(trip_interests_array)
            trip_interests_array = list(trip_interests_array)

            if not len(trip_interests_array):
                return Response({
                    'status': False,
                    'message': 'tripInterests can not be empty'
                }, status=400)

            for i in trip_interests_array:
                if trip_interest := TripInterest.objects.filter(id=i):
                    if trip_interest.first() not in user.trip_interest.all():
                        user.trip_interest.add(trip_interest.first())

            if not user.trip_interest.all().count():
                return Response({
                    "status": False,
                    "message": "tripInterests should be from the list."
                }, status=400)

            temp_token.user.sign_up_steps = 'Trip Interest Set'
            temp_token.user.save()

            return Response({
                'status': True,
                'message': 'Successfully added, Set Wander List',
                'tempToken': tempToken
            })
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': 'tripInterests is not properly Formatted',
                'field': 'tripInterests'
            }, status=400)
            



class SetWanderListView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        cities_array = request.data.get('cities', None)
        tempToken = request.data.get('tempToken', None)

        try:
            temp_token = TempToken.objects.get(token=tempToken)
            user = temp_token.user
        except TempToken.DoesNotExist:
            return Response({
                'status': False,
                'message': 'No Token Found or Token Expired',
                'field': 'tempToken'
            }, status=400)

        if not temp_token or not cities_array:
            return Response({
                'status': False,
                'message': 'tempToken and cities is required',
                'field': 'tempToken and cities'
            }, status=400)

        elif user.sign_up_steps == 'Wander List Set':
            return Response({
                'status': False,
                'goTo': 'tripInterest',
                'message': 'Cities Already Set, Set Profile'
            }, status=400)

        elif user.sign_up_steps != 'Trip Interest Set':
            return Response({
                'status': False,
                'goTo': 'login',
                'message': 'Login Again'
            }, status=400)
        
        try:
            cities_array = json.loads(cities_array)
            cities_array = list(cities_array)

            if not len(cities_array):
                return Response({
                    'status': False,
                    'message': 'tripInterests can not be empty',
                    'field': 'tripInterests'
                }, status=400)
            
            for i in cities_array:
                if cities := City.objects.filter(id=i):
                    if cities.first() not in user.interested_location.all():
                        user.interested_location.add(cities.first())

            if not user.interested_location.all().count():
                return Response({
                    "status": False,
                    "message": "cities should be from the list",
                    'field': 'cities'
                }, status=400)

            user.sign_up_steps = 'Wander List Set'
            user.save()

            token = get_tokens_for_user(user)
            userDict = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'verified_account': user.verified_account,
                "user_type": 'host' if user.is_host else 'traveller',
            }

            temp_token.delete()

            return Response({
                "status": True,
                "message": "Profile Added Successfully",
                "user": userDict,
                "token": token['access'],
                "refresh": token['refresh']
            }, status=200)


        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': 'wanderList is not properly Formatted'
            }, status=400)


from django.utils import timezone

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        phone = request.data.get('phone', None)
        if phone:
            user = MyUser.objects.filter(phone=phone)
            if user.exists():
                if not user.first().is_active:
                    return Response({"status": False, "message": "Account not Active, Contact your Company Head!"}, status=400)
            else:
                return Response({"status": False, "message": "Wrong Credentials!"}, status=400)
        else:
            return Response({
                "status": False,
                "message": "phone is required",
                "field": "phone"
            }, status=400)

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        TempToken.objects.filter(user=user).delete()

        if user.sign_up_steps == 'Wander List Set':

            # if user.last_login:
            #     first_login = False
            # else:
            #     first_login = True

            # user.last_login = timezone.now()
            # user.save()

            # token, created = Token.objects.get_or_create(user=user)
            token = get_tokens_for_user(user)

            userDict = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'verified_account': user.verified_account,
                "user_type": 'host' if user.is_host else 'traveller',
            }

            return Response({
                "status": True,
                "user": userDict,
                "token": token['access'],
                "refresh": token['refresh']
            }, status=200)

        elif user.sign_up_steps == 'Password Set':
            temp_token = TempToken(user=user, usage='Email')
            temp_token.save()
            return Response({
                'status': False,
                'goTo': 'email',
                'message': 'Add Email',
                'tempToken': temp_token.token
            }, status=400)

        elif user.sign_up_steps == 'Email Set':
            temp_token = TempToken(user=user, usage='Profile')
            temp_token.save()
            return Response({
                'status': False,
                'goTo': 'profile',
                'message': 'Set Profile',
                'email': temp_token.user.email,
                'tempToken': temp_token.token
            }, status=400)

        elif user.sign_up_steps == 'Travel Type Set':
            temp_token = TempToken(user=user, usage='Trip Interest')
            temp_token.save()
            return Response({
                'status': False,
                'goTo': 'travelInterest',
                'message': 'Set Travel Interest',
                'tempToken': temp_token.token
            }, status=400)

        elif user.sign_up_steps == 'Trip Interest Set':
            temp_token = TempToken(user=user, usage='Wander List')
            temp_token.save()
            return Response({
                'status': False,
                'goTo': 'wanderList',
                'message': 'Set Wander List',
                'tempToken': temp_token.token
            }, status=400)

        elif user.sign_up_steps == 'Profile Set':
            temp_token = TempToken(user=user, usage='Travel Type')
            temp_token.save()
            return Response({
                'status': False,
                'goTo': 'travelType',
                'message': 'Add Travel Type',
                'tempToken': temp_token.token
            }, status=400)

        else:
            return Response({
                'status': False,
                'goTo': 'signUp',
                'message': 'Sign Up First'
            }, status=400)



class LogoutView(APIView):

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({
                "status": False,
                "message": "refresh_token field is required!",
                "field": "refresh_token"
            }, status=400)

        try:
            blacklist_token(refresh_token)
        except rest_framework_simplejwt.exceptions.TokenError:
            return Response({
                "status": False,
                "message": "Token is invalid or expired",
            }, status=400)
        
        except Exception as e:
            print(e)
            return Response({
                "status": False,
                "message": "Token is invalid or expired",
            }, status=400)


        request.user.last_login = timezone.now()
        request.user.save()
        return Response({'status': True, 'Message': 'You have successfully logged out!'}, status=200)

class ForgotPasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        phone = request.data.get('phone', None)
        if not phone:
            return Response({"status": False, "message": "Phone is Required!", "field": "phone"}, status=400)
        try:
            user = MyUser.objects.get(phone=phone)
            if user.sign_up_steps != 'Wander List Set':
                return Response({
                    "status": False,
                    "goTo": "login",
                    "message": "SignUp Steps are incomplete"
                }, status=400)
        except MyUser.DoesNotExist:
            return Response({"status": False, "message": "No Account Found!"}, status=400)

        if not user.is_active:
            return Response({"status": False, "message": "User is Not Active, Activate your account first!"}, status=400)
        
        if user.is_admin:
            return Response({"status": False, "message": "Not Authorized to Login!"}, status=400)
        
        
        if user.sign_up_steps == 'OTP Sent':
            return Response({
                "status": False,
                "goTo": "signUp",
                "message": "Sign Up Again"
            }, status=400)
        
        if user.sign_up_steps == 'OTP Verified':
            return Response({
                "status": False,
                "goTo": "signUp",
                "message": "Sign Up Again"
            }, status=400)

        if Code.objects.filter(user=user).exists():
            if Code.objects.filter(user=user).first().usage == 'Register':
                return Response({"status": False, "message": "Account is not Verified, Verify it first!"}, status=400)
            Code.objects.get(user=user).delete()

        random_code = get_random_code()
        code = Code(user=user, confirmation_code=random_code, usage='Forgot')
        code.save()

        # response = sending_code(random_code, user.email, phone, 'forgot_password')
        response = True
        
        if response:
            return Response({"status": True, "message": "Check your email/phone for confirmation Code!"})
        else:
            return Response({"status": False, "message": "Something Went Wrong while sending OTP to {}, Please Try Again Later!".format(phone)}, status=400)

class CodeVerificationAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    
    
    def post(self, request):
        try:
            code = request.data.get('code', None)
            if not code:
                return Response({
                    "status": False,
                    "message": "Code is Required!",
                    "field": "code"
                }, status=400)

            phone = request.data.get('phone', None)
            if not phone:
                return Response({
                    "status": False,
                    "message": "Phone is Required!",
                    "field": "phone"
                }, status=400)

            users = MyUser.objects.filter(phone=phone)
            if not users.exists():
                return Response({"status": False, "message": "Email is Found!"}, status=400)

            if users.first().sign_up_steps != 'Wander List Set':
                return Response({
                    "status": False,
                    "goTo": "login",
                    "message": "SignUp Steps are incomplete"
                }, status=400)

            user_code = Code.objects.get(confirmation_code=code)

            if user_code.user != users.first():
                return Response({"status": False, "message": "Invalid details Provided"}, status=400)

            code_created_time = user_code.created_at
            if not check_expiration_code(code_created_time):
                user_code.delete()
                return Response({"status": False, "message": "Code Expired, Request a New One!", "field": "code"}, status=400)

            if user_code.usage == 'Register':
                user_code.user.is_verified = True
                user_code.user.save()
                user_code.delete()
                return Response({"status": True, "message": "Account has been verified successfully"})
            return Response({"status": True, "code": code, "phone": users.first().phone})
        except Code.DoesNotExist:
            return Response({"status": False, "message": "Wrong Confirmation Code!", "field": "code"}, status=400)


class NewPasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        code = request.data.get('code')

        if not code:
            return Response({
                "status": False,
                "message": "code is not there.",
                "field": "code"
            }, status=400)

        try:
            user_code = Code.objects.get(confirmation_code=code)
        except Code.DoesNotExist:
            return Response({
                "status": False,
                "message": "Wrong Confirmation Code!",
                "field": "code"
            }, status=400)

        code_created_time = user_code.created_at
        if not check_expiration_code(code_created_time):
            user_code.delete()
            return Response({
                "status": False,
                "message": "Code Expired, Request a New One!",
                "field": "code"
            }, status=400)

        try:
            password = request.data['new_password']
            confirm_password = request.data['confirm_password']
        except Exception as e:
            return Response({
                "status": False,
                "message": "Both Fields are required!",
                "field": "new_password and confirm_password"
                }, status=400)

        if len(password) < 8:
            return Response({
                'status': False,
                'message': 'Password must be atleast 8 characters'
            }, status=400)

        if password != confirm_password:
            return Response({"status": False, "message": "Passwords do not match"}, status=400)
        else:
            user = user_code.user
            if user.sign_up_steps != 'Wander List Set':
                return Response({
                    "status": False,
                    "goTo": "login",
                    "message": "SignUp Steps are incomplete"
                }, status=400)

            user.set_password(password)
            user.save()
            user_code.delete()
            return Response({"status": True, "message": "Password has been changed!"})

class UpdatePasswordAPIView(APIView):

    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                "status": False,
                "message": "Wrong old Password",
                "field": "old_password"
            }, status=400)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"status": True, "message": "Password has been successfully changed!"})
