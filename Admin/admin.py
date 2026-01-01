from django.contrib import admin

from .models import AdminNotice,SubscriptionHistory
admin.site.register(AdminNotice)
admin.site.register(SubscriptionHistory)