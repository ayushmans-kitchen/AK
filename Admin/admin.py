from django.contrib import admin

from .models import AdminNotice,CustomerHistory
# Register your models here.
admin.site.register(AdminNotice)
admin.site.register(CustomerHistory)