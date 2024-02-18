from account.models import MyUser
from rest_framework.views import APIView
from rest_framework.response import Response
from core.api.serializers import StayHostSerializer
from core.models import Profile

from migo.utils.customPaginations import CustomPagination

# from account.api.utils import sending_invite

class FollowAPIView(APIView):

    def post(self, request):
        try:
            id = request.data.get('user_id')
            user = MyUser.objects.select_related('profile').get(pk=id)
            if user.is_admin or user.is_superuser or user.is_staff:
                return Response({
                    "status": False,
                    "message": "Can't Follow"
                }, status=400)
        except MyUser.DoesNotExist:
            return Response({
                "status": False,
                "message": "No User Found!"
            }, status=400)

        logged_in_user = request.user
        logged_in_profile = logged_in_user.profile
        if request.user != user:
            if user in logged_in_profile.following.all():
                logged_in_profile.following.remove(user)
                logged_in_profile.save()
                return Response({'status': True, "message": "Now you are not following {}".format(user.name)}, status=201)
            else:
                logged_in_profile.following.add(user)
                logged_in_profile.save()
                return Response({'status': True, "message": "Now you are following {}".format(user.name)}, status=201)
        else:
            return Response({
                "status": False,
                "message": "You can't follow/unfollow yourself!"
            }, status=400)


class RemoveFollowerAPIView(APIView):

    def post(self, request):
        try:
            id = request.data.get('user_id')
            user = MyUser.objects.get(pk=id)
            if user.is_admin or user.is_superuser or user.is_staff:
                return Response({
                    "status": False,
                    "message": "Can't Follow"
                }, status=400)
        except MyUser.DoesNotExist:
                return Response({
                    "status": False,
                    "message": "Can't Follow"
                }, status=400)

        logged_in_user = request.user
        logged_in_profile = logged_in_user.profile
        if request.user != user:
            if logged_in_user in user.profile.following.all():
                user.profile.following.remove(logged_in_user)
                user.save()
                return Response({'status': True, "message": "You have removed {} from your followers list.".format(user.name)}, status=201)
            else:
                return Response({'status': False, "message": "User Not in your followers list."}, status=400)
        else:
            return Response({
                "status": False,
                "message": "You can't follow/unfollow yourself!"
            }, status=400)

class FollowersAPIView(APIView):

    def get(self, request):
        user = request.user
        followers = Profile.objects.filter(following__id__exact=user.id)
        serializer = StayHostSerializer(followers, many=True)
        return Response({
            "status": True,
            "data": serializer.data
        })

class FollowingsAPIView(APIView):

    def get(self, request):
        user = request.user
        followings = user.profile.following.all()
        profiles = []
        for u in followings:
            profiles.append(u.profile)
        serializer = StayHostSerializer(profiles, many=True)
        return Response({
            "status": True,
            "data": serializer.data
        })
