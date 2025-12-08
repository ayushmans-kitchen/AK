from django.contrib import admin
from django.urls import path, include

from Admin.views import gen_Lunch_record,gen_Dinner_record, admin_dashboard, service_list, admin_user_management, daily_report
from.views import home
from Customers import urls as csurls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(csurls)),

    
    path('lun/',gen_Lunch_record,name="lun record"),
    path('din/',gen_Dinner_record,name="din record"),

    path('admin-dashboard/',admin_dashboard,name='admin_dashboard'),

    path("service/<str:meal>/<str:service>/", service_list, name="service_list"),

    path("user-management/", admin_user_management, name="admin_user_management"),


    path("daily-report/", daily_report, name="daily_report"),

]
