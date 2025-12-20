from django.urls import path, include
from Admin.views import dashboard, service_details, subscribers, profile
from .backend_views import gen_Dinner_record,gen_Lunch_record,add_admin_message,delete_admin_notice
from Admin.views import dashboard, service_details, subscribers, profile,add_customer

urlpatterns = [
    path('dashboard/',dashboard,name='ayushman_dashboard'),
    path('service-details/',service_details,name='service_details'),
    path('subscribers/',subscribers,name='subscribers'),
    path('add-customer/',add_customer,name='add_customer'),
    path('profile/',profile,name='profile'),
    
    
    path('gen_Lunch_record/',gen_Lunch_record,name='gen_Lunch_record'),
    path('gen_Dinner_record/',gen_Dinner_record,name='gen_Dinner_record'),
    path('admin_notice/',add_admin_message,name='admin_notice'),
    path('admin_notice_delete/<int:mid>/', delete_admin_notice, name='admin_notice_delete'),
    
    
]
