from .test_setup import TestSetUp
from account.models import MyUser, Code


class TestView(TestSetUp):

    def test_user_cannot_register_with_no_data(self):
        res = self.client.post(self.register_url)
        self.assertEqual(res.status_code, 400)

    def test_user_cannot_register_with_invalid_phone_number(self):
        self.user_data['phone'] = "98989898"
        res = self.client.post(
            self.register_url, self.user_data, format='json')
        self.assertEqual(res.status_code, 400)

    def test_user_can_register_with_data(self):
        res = self.client.post(
            self.register_url, self.user_data, format='json')
        self.assertEqual(res.data["phone"], self.user_data["phone"])
        self.assertEqual(res.status_code, 201)

    def test_user_cannot_set_invalid_email(self):

        res = self.client.post(
            self.register_url, self.user_data, format='json')

        code = Code.objects.get(user__phone=res.data["phone"])    

        
        otp_body = {
            "phone": res.data["phone"],
            "otp": code.confirmation_code
        }
        
        res = self.client.post(self.otp_verify_url, otp_body)

        self.password_body["tempToken"] = res.data["tempToken"],

        res = self.client.post(self.set_password_url, self.password_body)

        self.email_body["email"] = "someemail.com"
        self.email_body["tempToken"] = res.data["tempToken"],

        res = self.client.post(self.set_email_url, self.email_body)

        self.assertEqual(res.status_code, 400)

    def test_user_cannot_set_different_passwords(self):

        res = self.client.post(
            self.register_url, self.user_data, format='json')

        code = Code.objects.get(user__phone=res.data["phone"])    

        
        otp_body = {
            "phone": res.data["phone"],
            "otp": code.confirmation_code
        }
        
        res = self.client.post(self.otp_verify_url, otp_body)

        self.password_body["tempToken"] = res.data["tempToken"],
        self.password_body["new_password"] = res.data["tempToken"],

        res = self.client.post(self.set_password_url, self.password_body)

        self.assertEqual(res.status_code, 400)
    
    def test_user_cannot_set_profile_with_invalid_email(self):

        res = self.client.post(
            self.register_url, self.user_data, format='json')

        code = Code.objects.get(user__phone=res.data["phone"])    

        
        otp_body = {
            "phone": res.data["phone"],
            "otp": code.confirmation_code
        }
        
        res = self.client.post(self.otp_verify_url, otp_body)

        self.password_body["tempToken"] = res.data["tempToken"],

        res = self.client.post(self.set_password_url, self.password_body)

        self.email_body["tempToken"] = res.data["tempToken"],

        res = self.client.post(self.set_email_url, self.email_body)

        self.profile_body["tempToken"] = res.data["tempToken"]
        self.profile_body["email"] = "test.com"

        res = self.client.post(self.set_profile_url, self.profile_body)
        
        self.assertEqual(res.status_code, 400)
    
    def test_user_sign_up_process_full(self):
        res = self.client.post(
            self.register_url, self.user_data, format='json')

        code = Code.objects.get(user__phone=res.data["phone"])    

        
        otp_body = {
            "phone": res.data["phone"],
            "otp": code.confirmation_code
        }
        
        res = self.client.post(self.otp_verify_url, otp_body)

        self.password_body["tempToken"] = res.data["tempToken"],

        res = self.client.post(self.set_password_url, self.password_body)

        self.email_body["tempToken"] = res.data["tempToken"],

        res = self.client.post(self.set_email_url, self.email_body)

        self.profile_body["tempToken"] = res.data["tempToken"],

        res = self.client.post(self.set_profile_url, self.profile_body)

        self.travel_types_body["tempToken"] = res.data["tempToken"],

        res = self.client.post(self.set_travel_types_url, self.travel_types_body)

        self.trip_interests_body["tempToken"] = res.data["tempToken"],

        res = self.client.post(self.set_trip_interests_url, self.trip_interests_body)

        self.wander_list_body["tempToken"] = res.data["tempToken"],

        res = self.client.post(self.set_wander_list_url, self.wander_list_body)

        self.assertEqual(res.status_code, 200)
        
