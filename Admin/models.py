from django.db import models
from Customers.models import Customer

SUBSCRIPTION_TYPE = (
    ("NORMAL30", "NORMAL30"),
    ("NORMAL60", "NORMAL60"),
    ("FLAGSHIP30", "FLAGSHIP30"),
    ("FLAGSHIP60", "FLAGSHIP60"),
    ("PREMIUM30", "PREMIUM30"),
    ("PREMIUM60", "PREMIUM60")
)

class AdminNotice(models.Model):
    message=models.CharField(max_length=500)
    date=models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.message} - {self.date}"
    

class CustomerHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_history")
    subscription_choice = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPE, default="NORMAL60")
    subscription_phase=models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    meal_history = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.customer.name} | "
            f"{self.subscription_phase}"
            f"{self.subscription_choice} | "
            f"renewal_date - {created_at} | "
        )


