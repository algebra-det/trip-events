from core.models import BankDetails, Profile
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework import exceptions

from account.models import MyUser

from rest_framework.authtoken.models import Token
import uuid
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenVerifySerializer
from rest_framework_simplejwt.state import token_backend

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super(CustomTokenRefreshSerializer, self).validate(attrs)
        decoded_payload = token_backend.decode(data['access'], verify=True)
        user_uid=decoded_payload['user_id']
        # add filter query
        data.update({'status': True})
        return data

class CustomTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        data = super(CustomTokenVerifySerializer, self).validate(attrs)
        print(data)
        data.update({'status': True, 'message': 'Token is Valid'})
        return data

class ProfileSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ('name', 'gender', 'dob', 'email', 'public_email', 'public_gender', 'public_dob')
        extra_kwargs = {
            'name': {'required': True},
            'gender': {'required': True},
            'dob': {'required': True},
        }
class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ('phone',)

    def validate(self, attrs):
        phone = attrs.get('phone', '')

        if not phone:
            raise serializers.ValidationError(
                { "phone": [
                    'Phone field is required'
                    ]
                }
            )

        if MyUser.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                { "phone": [
                    'phone number already exists.'
                    ]
                }
            )

        attrs['phone'] = int(phone)

        return attrs
    
    def save(self):

        account = MyUser(
            phone=self.validated_data['phone'],
        )
        account.set_password(str(uuid.uuid4()))
        account.is_staff = False
        account.is_verified = True
        account.is_superuser = False
        account.is_admin = False
        account.save()
        return account

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        phone = data.get('phone', '')
        password = data.get('password', '')

        if phone and password:
            user = authenticate(phone=phone, password=password)
            if user:
                if user.is_active:
                    if user.is_verified:
                        data['user'] = user
                    else:
                        message = 'Account is not verified, Verify it first!'
                        raise exceptions.ValidationError(message)
                            
                else:
                    message = 'Account is not activated !'
                    raise exceptions.ValidationError(message)
            else:
                message = 'Wrong Credentials!'
                raise exceptions.ValidationError(message)
        else:
            message = 'Both fields are required!'
            raise exceptions.ValidationError(message)
        return data


# class LogoutSerializer(serializers.Serializer):
#     refresh = serializers.CharField()

#     def validate(self, attr):
#         self.token = attr['refresh']
#         return attr
    
#     def save(self, **kwargs):
#         RefreshToken(self.token).blacklist()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    class Meta:
        fields = ['old_password', 'new_password', 'confirm_password']

    def validate(self, attrs):
        old_password = attrs.get('old_password', '')
        new_password = attrs.get('new_password', '')
        confirm_password = attrs.get('confirm_password', '')

        if not old_password:
            raise serializers.ValidationError({"old_password": ["old_password is required"]})

        if not new_password:
            raise serializers.ValidationError({"new_password": ["new_password is required"]})

        if not confirm_password:
            raise serializers.ValidationError({"confirm_new_password": ["confirm_new_password is required"]})

        if new_password!=confirm_password:
            raise serializers.ValidationError({"error": ["Passwords do not match!"]})

        if len(new_password) < 8:
            raise serializers.ValidationError({"error": ["Password must be more then 8 digits long"]})
        
        return attrs