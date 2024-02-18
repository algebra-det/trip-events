from django.test import TestCase
from account.models import MyUser

class TestModel(TestCase):

    def test_user_create(self):
        phone = "9898989898"
        user = MyUser.objects.create(phone=phone)
        user.set_password('newPassword21')
        user.save()

        self.assertEqual(str(user), phone)