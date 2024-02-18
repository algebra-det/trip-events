from rest_framework.test import APITestCase
from django.urls import reverse

class TestSetUp(APITestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.otp_verify_url = reverse('otp_verify')
        self.set_password_url = reverse('set_password')
        self.set_email_url = reverse('set_email')
        self.set_profile_url = reverse('set_profile')
        self.set_travel_types_url = reverse('set_travel_types')
        self.set_trip_interests_url = reverse('set_trip_interests')
        self.set_wander_list_url = reverse('set_wander_list')

        self.user_data = {
            'phone': '2342342342'
        }

        self.password_body = {
            "new_password": "newPassword21",
            "confirm_password": "newPassword21"
        }

        self.email_body = {
            "email": "test@123.com"
        }

        self.profile_body = {
            "name": "Akash Chauhan",
            "gender": "Male",
            "dob": "2021-09-2",
            "bio": "Some Bio",
            "bank_name": "DIGNITECH",
            "account_number": "98989898898",
            "ifsc_code": "DIG98765"
        }

        self.travel_types_body = {
            "travelTypes": "[1,2, 4]"
        }

        self.trip_interests_body = {
            "tripInterests": "[1,2, 4]"
        }

        self.wander_list_body = {
            "cities": "[1,2, 4]"
        }

        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()

