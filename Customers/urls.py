from django.urls import path 
from Customers.views import user_dashboard, user_history ,api_meal_selection

from .loginview import login_view

urlpatterns =[
    path('login/', login_view, name='login'),
    path('', user_dashboard,name="user_dashboard"),
    path('api/meal-selection/', api_meal_selection, name='api_meal_selection'),
    path('user-history', user_history,name="user_history"),
]