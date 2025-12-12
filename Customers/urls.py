from django.urls import path 
from Customers.views import user_dashboard, user_history,user_lunch_form,user_dinner_form

from .loginview import login_view

urlpatterns =[
    path('login/', login_view, name='login'),
    path('', user_dashboard,name="user_dashboard"),
    path('userlunch/', user_lunch_form,name="userlunch"),
    path('userdinner/', user_dinner_form,name="userdinner"),
    path('user-history', user_history,name="user_history"),
]