from django.urls import path, include
from Admin.views import admin_dashboard, service_list, daily_report, complete_report, dashboard, subscribers, profile

urlpatterns = [
    path('admin-dashboard/',admin_dashboard,name='admin_dashboard'),
    path("service/<str:meal>/<str:service>/", service_list, name="service_list"),
    path("daily-report/", daily_report, name="daily_report"),
    path("complete-report/", complete_report, name="complete_report"),



    path('dashboard/',dashboard,name='ayushman_dashboard'),
    path('subscribers/',subscribers,name='subscribers'),
    path('profile/',profile,name='profile'),

    
]
