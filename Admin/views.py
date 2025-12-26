import logging
from django.utils import timezone
from django.db.models import F
from django.db.models.functions import Greatest
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from Customers.models import Customer, LunchRecord, DinnerRecord, SERVICE_TYPE,SUBSCRIPTION_TYPE
from .models import AdminNotice
from django.shortcuts import render,redirect
from Customers.models import MEAL_MENU,FLAGSHIP_MENU_LUNCH,FLAGSHIP_MENU_DINNER,PREMIUM_MENU_LUNCH,PREMIUM_MENU_DINNER
from .backend_views import gen_Lunch_record,gen_Dinner_record
today = timezone.localdate()

all_menus_lunch = list(dict.fromkeys(MEAL_MENU + FLAGSHIP_MENU_LUNCH + PREMIUM_MENU_LUNCH))
all_menus_dinner = list(dict.fromkeys(MEAL_MENU + FLAGSHIP_MENU_DINNER + PREMIUM_MENU_DINNER))


@staff_member_required(login_url='/login/')
def dashboard(request):
    customers = Customer.objects.all()
    lunch_record = LunchRecord.objects.filter(for_date=today)
    dinner_record = DinnerRecord.objects.filter(for_date=today)
    admin_messgaes = AdminNotice.objects.all()


    menu_lunch_count = {}
    menu_dinner_count = {}

    for key, _ in all_menus_lunch:
        menu_lunch_count[key] = 0

    for key, _ in all_menus_dinner:
        menu_dinner_count[key] = 0

    for l in lunch_record:
        choice = l.meal_choice or l.FLAGSHIP_choice or l.PREMIUM_choice
        # print(choice)
        if choice in menu_lunch_count:
            menu_lunch_count[choice] += 1

    for d in dinner_record:
        choice = d.meal_choice or d.FLAGSHIP_choice or d.PREMIUM_choice
        # print(choice)
        if choice in menu_dinner_count:
            menu_dinner_count[choice] += 1

    context={
        'total_customers':customers.exclude(is_staff=True,is_superuser=True).count(),
        'total_inactive_customers':customers.filter(user_status_active=False,paused_subscription=False,is_staff=False,is_superuser=False).count(),
        'total_plan_end_customers':customers.filter(paused_subscription=True,is_staff=False,is_superuser=False).count(),

        'total_lunch':lunch_record.exclude(service_choice="Cancel").count(),
        'lunch_dinein':lunch_record.filter(service_choice="DineIn").count(),
        'lunch_delivery':lunch_record.filter(service_choice="Delivery").count(),
        'lunch_pickup':lunch_record.filter(service_choice="PickUp").count(),
        'lunch_cancelled':lunch_record.filter(service_choice="Cancel").count(),
        'lunch_inactive':customers.filter(lunch_status_active=True,user_status_active=False,paused_subscription=False,is_staff=False,is_superuser=False).count(),
        'lunch_default_need':customers.filter(user_status_active=True,lunch_status_active=True,is_staff=False,is_superuser=False).exclude(lunch_records__for_date=today).count(),

        'total_dinner':dinner_record.exclude(service_choice="Cancel").count(),
        'dinner_dinein':dinner_record.filter(service_choice="DineIn").count(),
        'dinner_delivery':dinner_record.filter(service_choice="Delivery").count(),
        'dinner_pickup':dinner_record.filter(service_choice="PickUp").count(),
        'dinner_cancelled':dinner_record.filter(service_choice="Cancel").count(),
        'dinner_inactive':customers.filter(dinner_status_active=True,user_status_active=False,paused_subscription=False,is_staff=False,is_superuser=False).count(),
        'dinner_default_need':customers.filter(user_status_active=True,dinner_status_active=True,is_staff=False,is_superuser=False).exclude(dinner_records__for_date=today).count(),

        "menu_lunch_count": menu_lunch_count,
        "menu_dinner_count": menu_dinner_count,

        'low_balance_customer':customers.filter(meal_balance__lte=6,is_staff=False,is_superuser=False),
        'admin_messgaes':admin_messgaes,
    }
    return render(request,"Admin/dashboard.html",context)



@staff_member_required(login_url='/login/')
def service_details(request, dayTime, service):
    if dayTime == "Lunch":
        if service=="Total":
            result = LunchRecord.objects.filter(for_date = today).exclude(service_choice="Cancel")
        else:
            result = LunchRecord.objects.filter(for_date = today,service_choice=service)
    if dayTime == "Dinner":
        if service=="Total":
            result = DinnerRecord.objects.filter(for_date = today).exclude(service_choice="Cancel")
        else:
            result = DinnerRecord.objects.filter(for_date = today,service_choice=service)
    if service == "Cancel":
        cancelled_page=True
    else:
        cancelled_page=False
    
    # print(all_menus_lunch)
    # print(all_menus_dinner)
    context = {
        "records": result,
        "dayTime": dayTime,
        "service": service,
        "cancelled_page":cancelled_page,
        "all_menus_lunch": all_menus_lunch,
        "all_menus_dinner": all_menus_dinner,

    }    
    return render(request,"Admin/service-details.html", context)

    

@staff_member_required(login_url='/login/')
def subscribers(request):
    return render(request,"Admin/subscribers.html")

@staff_member_required(login_url='/login/')
def add_customer(request):
    if request.method == "POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        password=request.POST.get("password")
        address=request.POST.get("address")
        subscription_choice=request.POST.get("subscription_choice")
        meal_balance=request.POST.get("meal_balance")
        default_lunch_service_choice=request.POST.get("default_lunch_service_choice")
        default_dinner_service_choice=request.POST.get("default_dinner_service_choice")

        try:
            with transaction.atomic():
                Customer.objects.create_user(
                email=email,
                name=name,
                phone=phone,
                password=password,
                address=address,
                subscription_choice=subscription_choice,
                meal_balance=meal_balance,
                default_lunch_service_choice=default_lunch_service_choice,
                default_dinner_service_choice=default_dinner_service_choice)
        except Exception as e:
            logger.exception("Unexpected error in addind Customer : %s", e)
            return JsonResponse({"error": str(e)}, status=500)
    return render(request,"Admin/add-customer.html")


@staff_member_required(login_url='/login/')
def customer_profile(request,uid):
    user=get_object_or_404(Customer,pk=uid)
    return render(request,"Admin/customer_profile.html",{'user':user})

