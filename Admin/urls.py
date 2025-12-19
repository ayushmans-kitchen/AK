from django.urls import path, include
from Admin.views import dashboard, service_details, subscribers, profile

urlpatterns = [
    path('dashboard/',dashboard,name='ayushman_dashboard'),
    path('service-details/',service_details,name='service_details'),
    path('subscribers/',subscribers,name='subscribers'),
    path('profile/',profile,name='profile'),

    
]
