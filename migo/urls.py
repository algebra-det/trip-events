from django.contrib import admin
from django.views.generic.base import TemplateView
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html')),
]

# MISC APIs
from misc.api import api_views as misc_views

urlpatterns += [
    path('api/v1/misc/get_cities/', misc_views.CityList.as_view(), name="get_cities"),
    path('api/v1/misc/get_travel_types/', misc_views.TravelTypeList.as_view(), name="get_travel_types"),
    path('api/v1/misc/get_trip_interests/', misc_views.TripInterestList.as_view(), name="get_trip_interests"),
]

# Account APIs
from account.api import api_views as account_views
from rest_framework_simplejwt import views as jwt_views

urlpatterns += [
    path('api/v1/account/me/', account_views.CurrentUserView.as_view(), name='current_user'),
    path('api/v1/account/register/', account_views.RegisterView.as_view(), name='register'),
    path('api/v1/account/otp_verify/', account_views.OTPVerifyView.as_view(), name='otp_verify'),
    path('api/v1/account/set_password/', account_views.SetPasswordView.as_view(), name='set_password'),
    path('api/v1/account/set_email/', account_views.SetEmail.as_view(), name='set_email'),
    path('api/v1/account/set_profile/', account_views.SetProfileView.as_view(), name='set_profile'),
    path('api/v1/account/set_travel_types/', account_views.SetTravelTypeView.as_view(), name='set_travel_types'),
    path('api/v1/account/set_trip_interests/', account_views.SetTripInterestsView.as_view(), name='set_trip_interests'),
    path('api/v1/account/set_wander_list/', account_views.SetWanderListView.as_view(), name='set_wander_list'),
    path('api/v1/account/login/', account_views.LoginView.as_view(), name='login'),
    path('api/v1/account/logout/', account_views.LogoutView.as_view()),
    path('api/v1/account/me/', account_views.CurrentUserView.as_view()),
    path('api/v1/account/forgot-password/', account_views.ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('api/v1/account/verify-code/', account_views.CodeVerificationAPIView.as_view(), name="verify-code"),
    path('api/v1/account/new-password/', account_views.NewPasswordAPIView.as_view(), name="new-password"),
    path('api/v1/account/update-password/', account_views.UpdatePasswordAPIView.as_view(), name="update-password"),

    path('api/v1/account/update-profile/', account_views.UpdateProfileView.as_view(), name='update_profile'),

    path('api/v1/account/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/v1/account/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/account/token/refresh/', account_views.TokenRefreshAPIView.as_view(), name='token_refresh'),
    # path('api/v1/account/token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify')
    path('api/v1/account/token/verify/', account_views.TokenVerifyAPIView.as_view(), name='token_verify')
]

# Profile APIs
from core.api import api_views as core_views

urlpatterns += [
    path('api/v1/profile/follow_unfollow/', core_views.FollowAPIView.as_view(), name="follow_unfollow_user"),
    path('api/v1/profile/followers/remove/', core_views.RemoveFollowerAPIView.as_view(), name="remove_follower"),
    path('api/v1/profile/followers/', core_views.FollowersAPIView.as_view(), name="followers"),
    path('api/v1/profile/followings/', core_views.FollowingsAPIView.as_view(), name="followings"),
]


# Stay APIs
from stay.api import api_views as stay_views

urlpatterns += [
    path('api/v1/stay/create/', stay_views.CreateStayAPIView.as_view(), name="create_stay"),
    path('api/v1/stay/update/<int:stay_id>/', stay_views.UpdateStayAPIView.as_view(), name="update_stay"),
    path('api/v1/stay/details/<int:stay_id>/', stay_views.StayDetailsAPIView.as_view(), name="stay_details"),
    path('api/v1/stay/image/<int:image_id>/delete/', stay_views.DeleteStayImageAPIView.as_view(), name="stay_image_delete"),
    path('api/v1/stay/', stay_views.StayListingAPIView.as_view(), name="stay_listing"),
    path('api/v1/stay/my-stays/', stay_views.StayListingOfHostAPIView.as_view(), name="my_stays"),
    path('api/v1/stay/delete/<int:stay_id>/', stay_views.StayDeleteAPIView.as_view(), name="stay_delete"),
    path('api/v1/stay/booking/create/', stay_views.BookingCreateAPIView.as_view(), name="stay_booking_create"),
    path('api/v1/stay/booking/requests/', stay_views.BookingRequestListingAPIView.as_view(), name="booking_requests"),
    path('api/v1/stay/booking/approve_reject/', stay_views.BookingApproveRejectAPIView.as_view(), name="booking_approve_reject"),
    path('api/v1/stay/booking/', stay_views.BookingstListingAPIView.as_view(), name="booking_listing"),
    path('api/v1/stay/booking/cancel/<int:booking_id>/', stay_views.BookingCancelAPIView.as_view(), name="booking_cancel"),
    path('api/v1/stay/booking/my-bookings/', stay_views.BookingUserListingAPIView.as_view(), name="booking_user_listing"),
    path('api/v1/stay/review/create/', stay_views.ReviewCreateAPIView.as_view(), name="stay_review_create"),
]


# Event APIs
from event.api import api_views as event_views

urlpatterns += [
    path('api/v1/event/create/', event_views.EventCreateAPIView.as_view(), name="create_event"),
    path('api/v1/event/update/<int:event_id>/', event_views.EventUpdateAPIView.as_view(), name="update_event"),
    path('api/v1/event/details/<int:event_id>/', event_views.EventDetailsAPIView.as_view(), name="event_details"),
    path('api/v1/event/delete/<int:event_id>/', event_views.EventDeleteAPIView.as_view(), name="event_delete"),
    path('api/v1/event/image/<int:image_id>/delete/', event_views.DeleteEventImageAPIView.as_view(), name="event_image_delete"),
    path('api/v1/event/', event_views.EventListingAPIView.as_view(), name="event_listing"),
    path('api/v1/event/my-events/', event_views.EventListingOfHostAPIView.as_view(), name="event_listing_of_host"),
    path('api/v1/event/booking/create/', event_views.EventBookingCreateAPIView.as_view(), name="event_booking_create"),
    path('api/v1/event/booking/requests/', event_views.EventBookingRequestsAPIView.as_view(), name="event_booking_requests"),
    path('api/v1/event/booking/my-bookings/', event_views.EventBookingUserListingAPIView.as_view(), name="event_my_booking"),
    path('api/v1/event/booking/approve_reject/', event_views.EventBookingApproveRejectAPIView.as_view(), name="event_approve_reject"),
    path('api/v1/event/booking/', event_views.EventBookingstListingAPIView.as_view(), name="event_bookings_listing"),
    path('api/v1/event/booking/cancel/<int:booking_id>/', event_views.EventBookingCancelAPIView.as_view(), name="event_booking_cancel"),
]

# Trip APIs
from trip.api import api_views as trip_views
urlpatterns += [
    path('api/v1/trip/create/', trip_views.TripCreateAPIView.as_view(), name="trip_create"),
    path('api/v1/trip/<int:trip_id>/', trip_views.TripDetailAPIView.as_view(), name="trip_details"),
    path('api/v1/trip/add-member/', trip_views.AddMemberToTripAPIView.as_view(), name="add_member_to_trip"),
    path('api/v1/trip/remove-member/', trip_views.RemoveMemberToTripAPIView.as_view(), name="remove_member_from_trip"),
    path('api/v1/trip/planner/create/', trip_views.PlannerCreateAPIView.as_view(), name="planner_create"),
    path('api/v1/trip/planner/details/<int:planner_id>/', trip_views.PlannerDetailsAPIView.as_view(), name="planner_details"),
    path('api/v1/trip/<int:trip_id>/planner/', trip_views.TripPlannerListingAPIView.as_view(), name="trip_planners"),
    path('api/v1/trip/log/create/', trip_views.TripLogCreateAPIView.as_view(), name="trip_planners"),
]

from django.conf.urls.static import static
from django.conf import settings

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
