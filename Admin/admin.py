from django.contrib import admin

from .models import AdminNotice,MealHistory
admin.site.register(AdminNotice)
admin.site.register(MealHistory)