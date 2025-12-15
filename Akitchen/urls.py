from django.contrib import admin
from django.urls import path, include

from Admin.views import admin_dashboard, service_list, admin_user_management, daily_report, complete_report
from.views import home
from Customers import urls as csurls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(csurls)),

    path('admin-dashboard/',admin_dashboard,name='admin_dashboard'),

    path("service/<str:meal>/<str:service>/", service_list, name="service_list"),

    path("user-management/", admin_user_management, name="admin_user_management"),


    path("daily-report/", daily_report, name="daily_report"),
    path("complete-report/", complete_report, name="complete_report"),

]
