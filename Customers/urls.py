from django.urls import path 
from Customers.views import user_dashboard,user_profile, user_history,user_lunch_form,user_dinner_form,user_sunday_lunch_form

from .loginview import login_view,logout_view

urlpatterns =[
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('', user_dashboard,name="user_dashboard"),
    path('user-profile', user_profile,name="user_profile"),
    path('user-history', user_history,name="user_history"),
    
    path('userlunch/', user_lunch_form,name="userlunch"),
    path('usersundaylunch/', user_sunday_lunch_form,name="usersundaylunch"),
    path('userdinner/', user_dinner_form,name="userdinner"),
]