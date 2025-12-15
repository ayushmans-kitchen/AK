from django.contrib import admin

from .models import AdminNotice,CustomerHistory
admin.site.register(AdminNotice)
admin.site.register(CustomerHistory)