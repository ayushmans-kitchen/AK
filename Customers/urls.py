from django.urls import path 
from Customers.views import user_dashboard, user_history



urlpatterns =[
    path('', user_dashboard,name="user_dashboard"),
    path('user-history', user_history,name="user_history"),
]