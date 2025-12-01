from django.contrib import admin
from django.urls import path

from Admin.views import gen_Lunch_record,gen_Dinner_record
from.views import home
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('lun/',gen_Lunch_record,name="lun record"),
    path('din/',gen_Dinner_record,name="din record")
]
