from django.shortcuts import render
from django.http import JsonResponse
from Admin.models import MealHistory

def home(request):
    a=MealHistory.objects.get(customer=4).meal_history
    return JsonResponse(a)