from django.shortcuts import render
from django.http import JsonResponse
from Admin.models import SubscriptionHistory

def home(request):
    a=SubscriptionHistory.objects.get(customer=4).meal_history
    return JsonResponse(a)