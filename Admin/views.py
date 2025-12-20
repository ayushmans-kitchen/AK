import logging
from django.utils import timezone
from django.db.models import F
from django.db.models.functions import Greatest
from django.db import transaction
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from Customers.models import Customer, LunchRecord, DinnerRecord, SERVICE_TYPE,SUBSCRIPTION_TYPE
from .models import AdminNotice
from django.shortcuts import render,redirect

today = timezone.localdate()

from .backend_views import gen_Lunch_record,gen_Dinner_record

@staff_member_required(login_url='/login/')
def dashboard(request):
    customers = Customer.objects.all()
    lunch_record = LunchRecord.objects.filter(for_date=today)
    dinner_record = DinnerRecord.objects.filter(for_date=today)
    admin_messgaes = AdminNotice.objects.all()
    L_MAP = {
        "VEG": "VEG",
        "NON_VEG": "NON_VEG",
        "PANEER": "PANEER",
        "MUSHROOM": "MUSHROOM",
        "CHICKEN": "CHICKEN",
        "EGG": "EGG",
        "PRAWN": "PRAWN",
        "FISH": "FISH",
    }

    D_MAP = {
        "VEG": "VEG",
        "NON_VEG": "NON_VEG",
        "PANEER": "PANEER",
        "MUSHROOM": "MUSHROOM",
        "CHICKEN": "CHICKEN",
        "EGG": "EGG",
    }

    # initialize counters
    L_FOOD_CHOICES = {v: 0 for v in L_MAP.values()}
    D_FOOD_CHOICES = {v: 0 for v in D_MAP.values()}

    # populate lunch
    for l in lunch_record:
        choice = l.meal_choice or l.FLAGSHIP_choice or l.PREMIUM_choice
        if choice in L_MAP:
            L_FOOD_CHOICES[L_MAP[choice]] += 1

    # populate dinner
    for d in dinner_record:
        choice = d.meal_choice or d.FLAGSHIP_choice or d.PREMIUM_choice
        if choice in D_MAP:
            D_FOOD_CHOICES[D_MAP[choice]] += 1


    context={
        'total_customers':customers.exclude(is_staff=True,is_superuser=True).count(),
        'total_inactive_customers':customers.filter(user_status_active=False,paused_subscription=False,is_staff=False,is_superuser=False).count(),
        'total_plan_end_customers':customers.filter(paused_subscription=True,is_staff=False,is_superuser=False).count(),

        'total_lunch':lunch_record.count(),
        'lunch_dinein':lunch_record.filter(service_choice="DineIn").count(),
        'lunch_delivery':lunch_record.filter(service_choice="Delivery").count(),
        'lunch_pickup':lunch_record.filter(service_choice="PickUp").count(),
        'lunch_cancelled':lunch_record.filter(service_choice="Cancel").count(),
        'lunch_inactive':customers.filter(lunch_status_active=True,user_status_active=False,paused_subscription=False,is_staff=False,is_superuser=False).count(),
        'lunch_default_need':customers.filter(user_status_active=True,lunch_status_active=True,is_staff=False,is_superuser=False).exclude(lunch_records__for_date=today).count(),

        'total_dinner':dinner_record.count(),
        'dinner_dinein':dinner_record.filter(service_choice="DineIn").count(),
        'dinner_delivery':dinner_record.filter(service_choice="Delivery").count(),
        'dinner_pickup':dinner_record.filter(service_choice="PickUp").count(),
        'dinner_cancelled':dinner_record.filter(service_choice="Cancel").count(),
        'dinner_inactive':customers.filter(dinner_status_active=True,user_status_active=False,paused_subscription=False,is_staff=False,is_superuser=False).count(),
        'dinner_default_need':customers.filter(user_status_active=True,dinner_status_active=True,is_active=False,is_superuser=False).exclude(dinner_records__for_date=today).count(),

        "l_food": L_FOOD_CHOICES,
        "d_food": D_FOOD_CHOICES,

        'low_balance_customer':customers.filter(meal_balance__lte=6),
        'admin_messgaes':admin_messgaes,
    }
    return render(request,"Admin/dashboard.html",context)



@staff_member_required(login_url='/login/')
def service_details(request):
    return render(request,"Admin/service-details.html")

    

@staff_member_required(login_url='/login/')
def subscribers(request):
    return render(request,"Admin/subscribers.html")

@staff_member_required(login_url='/login/')
def add_customer(request):
    return render(request,"Admin/add-customer.html")


@staff_member_required(login_url='/login/')
def profile(request):
    return render(request,"Admin/profile.html")

