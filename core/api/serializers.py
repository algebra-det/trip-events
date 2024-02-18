from core.models import Profile, BankDetails

from rest_framework import serializers

class ProfileBioSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('bio', 'image')
        extra_kwargs = {'bio': {'required': True}}

class BankDetailsSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankDetails
        fields = ('bank_name', 'account_number', 'ifsc_code')
        extra_kwargs = {
            'bank_name': {'required': True},
            'account_number': {'required': True},
            'ifsc_code': {'required': True},
        }

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('created_at', 'updated_at')


class StayHostSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('name', 'followers', 'followings', 'user_id', 'image')
    
    def get_user_id(self, profile):
        return profile.user.id
    
    def get_name(self, profile):
        return profile.user.name
    
    def get_followers(self, profile):
        return Profile.objects.filter(following__id__exact=profile.user.id).count()
    
    def get_followings(self, profile):
        return profile.following.all().count()
    
    def get_image(self, profile):
        return profile.image.url