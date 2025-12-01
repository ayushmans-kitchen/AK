from django.contrib import admin

# Register your models here.
from .models import Customer,LunchRecord,DinnerRecord


admin.site.register(Customer)
admin.site.register(LunchRecord)
admin.site.register(DinnerRecord)