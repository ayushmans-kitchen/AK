from django.urls import path, include
from .backend_views import gen_Dinner_record,gen_Lunch_record,add_admin_message,delete_admin_notice,gen_sunday_record
from Admin.views import dashboard, service_details, subscribers,add_customer,customer_profile,customer_list,meal_record,track_subscription,track_subscription_details,update_meal_record

urlpatterns = [
    path('dashboard/',dashboard,name='ayushman_dashboard'),
    path('service-details/',service_details,name='service_details'),
    path('service-details/<str:service>/<str:dayTime>/',service_details, name='service_details'),

    path('customer_lists/<str:types>/',customer_list, name='customer_list'),

    path('subscribers/',subscribers,name='subscribers'),
    path('add-customer/',add_customer,name='add_customer'),
    path('customer_profile/<int:uid>/',customer_profile, name='customer_profile'),


    path('meal-record/',meal_record, name='meal_record'),
    path('update_meal_record/<str:selected_meal>/<int:ldid>',update_meal_record, name='update_meal_record'),

    path('track-subscription/',track_subscription, name='track_subscription'),
    path('track_subscription_details/<int:sid>/',track_subscription_details, name='track_subscription_details'),
    
    
    path('gen_Lunch_record/',gen_Lunch_record,name='gen_Lunch_record'),
    path('gen_sunday_record/',gen_sunday_record,name='gen_sunday_record'),
    path('gen_Dinner_record/',gen_Dinner_record,name='gen_Dinner_record'),
    path('admin_notice/',add_admin_message,name='admin_notice'),
    path('admin_notice_delete/<int:mid>/', delete_admin_notice, name='admin_notice_delete'),
    
    
]
