from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from misc.models import TripInterest, TravelType, City
import uuid



GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)

class MyUserManager(BaseUserManager):
    def create_user(self, phone, email=None, name=None, dob=None, password=None):
        if not phone:
            raise ValueError('Phone Number is Required')

        user = self.model(
            email = self.normalize_email(email),
            name = name,
            phone = phone,
            dob = dob
            )
        user.is_staff = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, email=None, name=None, dob=None, password=None):
        user = self.create_user(
            email = email,
            name = name,
            phone=phone,
            dob=dob,
            password = password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

SIGN_UP_STEPS = (
    ('OTP Sent', 'OTP Sent'),
    ('OTP Verified', 'OTP Verified'),
    ('Password Set', 'Password Set'),
    ('Email Set', 'Email Set'),
    ('Profile Set', 'Profile Set'),
    ('Travel Type Set', 'Travel Type Set'),
    ('Trip Interest Set', 'Trip Interest Set'),
    ('Wander List Set', 'Wander List Set'),
)

class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='Email Address', max_length=60, null=True, blank=True)
    name = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(unique=True, max_length=10)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    trip_interest = models.ManyToManyField(TripInterest, default=None, blank=True,)
    travel_type = models.ManyToManyField(TravelType, default=None, blank=True,)
    interested_location = models.ManyToManyField(City, default=None, blank=True,)
    verified_account = models.BooleanField(default=False)
    sign_up_steps = models.CharField(max_length=20, choices=SIGN_UP_STEPS, default='OTP Sent')
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_host = models.BooleanField(default=False)
    location_name = models.CharField(max_length=200, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    location_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    public_email = models.BooleanField(default=False)
    public_gender = models.BooleanField(default=False)
    public_dob = models.BooleanField(default=False)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return str(self.phone) or ''

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


TOKEN_CHOICES = (
    ('Password', 'Password'),
    ('Email', 'Email'),
    ('Profile', 'Profile'),
    ('Travel Type', 'Travel Type'),
    ('Trip Interest', 'Trip Interest'),
    ('Wander List', 'Wander List'),
)

class TempToken(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='temp_token')
    token = models.CharField(max_length=100, default=uuid.uuid4)
    usage = models.CharField(max_length=20, choices=TOKEN_CHOICES, default='Password')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} - {}'.format(self.user.phone, self.token)


CODE_CHOICES = (
    ('Register', 'Register'),
    ('Forgot', 'Forgot'),
)

class Code(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    confirmation_code = models.CharField(max_length=4)
    usage = models.CharField(max_length=20, choices=CODE_CHOICES, default='Register')

    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.phone

    def phone(self):
        return self.user.phone