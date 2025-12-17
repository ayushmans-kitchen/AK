from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

SUBSCRIPTION_TYPE = (
    ("NORMAL30", "NORMAL30"),
    ("NORMAL60", "NORMAL60"),
    ("FLAGSHIP30", "FLAGSHIP30"),
    ("FLAGSHIP60", "FLAGSHIP60"),
    ("PREMIUM30", "PREMIUM30"),
    ("PREMIUM60", "PREMIUM60")
)

SERVICE_TYPE = (
    ("DineIn", "DineIn"),
    ("PickUp", "PickUp"),
    ("Delivery", "Delivery"),
    ("Cancel", "Cancel"),
)

MEAL_MENU = (
    ("NONE","NONE"),
    ("VEG", "VEG"),
    ("NON-VEG", "NON-VEG"),
)

FLAGSHIP_MENU_LUNCH=(
    ("NONE","NONE"),
    ("PANEER","PANEER"),
    ("MUSHROOM","MUSHROOM"),
    ("CHICKEN","CHICKEN"),
)

FLAGSHIP_MENU_DINNER=(
    ("NONE","NONE"),
    ("PANEER","PANEER"),
    ("MUSHROOM","MUSHROOM"),
    ("CHICKEN","CHICKEN"),
)
PREMIUM_MENU_LUNCH=(
    ("NONE","NONE"),
    ("PANEER","PANEER"),
    ("MUSHROOM","MUSHROOM"),
    ("CHICKEN","CHICKEN"),
    ("EGG","EGG"),
    ("PRAWN","PRAWN"),
    ("FISH","FISH"),
    ("VEG","VEG"),
)
PREMIUM_MENU_DINNER=(
    ("NONE","NONE"),
    ("PANEER","PANEER"),
    ("MUSHROOM","MUSHROOM"),
    ("CHICKEN","CHICKEN"),
    ("EGG","EGG"),
    ("VEG","VEG"),
)

class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    profile_updated_at = models.DateTimeField(auto_now=True)
    subscription_phase=models.IntegerField(default=1)
    
    meal_balance = models.IntegerField(default=0)
    user_status_active = models.BooleanField(default=True)
    lunch_status_active = models.BooleanField(default=True)
    dinner_status_active = models.BooleanField(default=True)
    paused_subscription = models.BooleanField(default=False)

    subscription_choice = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPE, default="NORMAL60")
    default_lunch_service_choice = models.CharField(max_length=20, choices=SERVICE_TYPE, default="DineIn")
    default_dinner_service_choice = models.CharField(max_length=20, choices=SERVICE_TYPE, default="DineIn")
    default_meal_choice = models.CharField(max_length=20, choices=MEAL_MENU, default="NONE")

    FLAGSHIP_MENU_LUNCH_default_choice = models.CharField(max_length=20, choices=FLAGSHIP_MENU_LUNCH, default="NONE")
    FLAGSHIP_MENU_DINNER_default_choice = models.CharField(max_length=20, choices=FLAGSHIP_MENU_DINNER, default="NONE")
    PREMIUM_MENU_LUNCH_default_choice = models.CharField(max_length=20, choices=PREMIUM_MENU_LUNCH, default="NONE")
    PREMIUM_MENU_DINNER_default_choice = models.CharField(max_length=20, choices=PREMIUM_MENU_DINNER, default="NONE")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = CustomerManager()

    @property
    def total_meals(self):
        if self.subscription_choice in ["NORMAL30","FLAGSHIP30","PREMIUM30"]:
            return 30 
        else :
            return 60

    def __str__(self):
        return f"{self.name} ({self.subscription_choice}):balance={self.meal_balance}  - {self.email}"

class LunchRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="lunch_records")
    for_date = models.DateField()
    meal_num_used = models.IntegerField()
    service_choice = models.CharField(max_length=20, choices=SERVICE_TYPE)

    meal_choice = models.CharField(max_length=20, choices=MEAL_MENU,null=True,blank=True,default="NONE")
    FLAGSHIP_choice = models.CharField(max_length=20, choices=FLAGSHIP_MENU_LUNCH,null=True,blank=True,default="NONE")
    PREMIUM_choice = models.CharField(max_length=20, choices=PREMIUM_MENU_LUNCH,null=True,blank=True,default="NONE")
    
    decrement_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.name} - {self.service_choice} - {self.for_date} - {self.meal_num_used}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["customer", "for_date"], name="unique_lunch_per_customer_per_day")
        ]


class DinnerRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="dinner_records")
    for_date = models.DateField()
    meal_num_used = models.IntegerField()
    service_choice = models.CharField(max_length=20, choices=SERVICE_TYPE)

    meal_choice = models.CharField(max_length=20, choices=MEAL_MENU,null=True,blank=True,default="NONE")
    FLAGSHIP_choice = models.CharField(max_length=20, choices=FLAGSHIP_MENU_DINNER,null=True,blank=True,default="NONE")
    PREMIUM_choice = models.CharField(max_length=20, choices=PREMIUM_MENU_DINNER,null=True,blank=True,default="NONE")

    decrement_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.name} - {self.service_choice} - {self.for_date} - {self.meal_num_used}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["customer", "for_date"], name="unique_dinner_per_customer_per_day")
        ]
