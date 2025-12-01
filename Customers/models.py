from django.db import models

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

MEAL_TYPE = (
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


class Customer(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    meal_balance = models.IntegerField()
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_updated_at = models.DateTimeField(auto_now=True)

    user_status_active = models.BooleanField(default=True)
    lunch_status_active = models.BooleanField(default=True)
    dinner_status_active = models.BooleanField(default=True)
    low_balance_status_active = models.BooleanField(default=False)

    subscription_choice = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPE, default="NORMAL60")
    default_service_choice = models.CharField(max_length=20, choices=SERVICE_TYPE, default="DineIn")
    default_meal_choice = models.CharField(max_length=20, choices=MEAL_TYPE, default="VEG")
    
    
    FLAGSHIP_MENU_LUNCH_default_choice = models.CharField(max_length=20, choices=FLAGSHIP_MENU_LUNCH, default="NONE")
    FLAGSHIP_MENU_DINNER_default_choice = models.CharField(max_length=20, choices=FLAGSHIP_MENU_DINNER, default="NONE")
    PREMIUM_MENU_LUNCH_default_choice = models.CharField(max_length=20, choices=PREMIUM_MENU_LUNCH, default="NONE")
    PREMIUM_MENU_DINNER_default_choice = models.CharField(max_length=20, choices=PREMIUM_MENU_DINNER, default="NONE")




    def __str__(self):
        return f"{self.name} - {self.address} - remain({self.meal_balance})"


class LunchRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="lunch_records")
    # remove auto_now_add so we can explicitly set for_date
    for_date = models.DateField()
    meal_choice = models.CharField(max_length=20, choices=MEAL_TYPE)
    meal_num_used = models.IntegerField()
    service_choice = models.CharField(max_length=20, choices=SERVICE_TYPE)

    FLAGSHIP_choice = models.CharField(max_length=20, choices=FLAGSHIP_MENU_LUNCH,null=True,blank=True)
    PREMIUM_choice = models.CharField(max_length=20, choices=PREMIUM_MENU_LUNCH,null=True,blank=True)
    
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
    meal_choice = models.CharField(max_length=20, choices=MEAL_TYPE)
    meal_num_used = models.IntegerField()
    service_choice = models.CharField(max_length=20, choices=SERVICE_TYPE)

    FLAGSHIP_choice = models.CharField(max_length=20, choices=FLAGSHIP_MENU_DINNER,null=True,blank=True)
    PREMIUM_choice = models.CharField(max_length=20, choices=PREMIUM_MENU_DINNER,null=True,blank=True)

    decrement_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.name} - {self.service_choice} - {self.for_date} - {self.meal_num_used}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["customer", "for_date"], name="unique_dinner_per_customer_per_day")
        ]
