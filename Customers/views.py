from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db import transaction
import json

from datetime import timedelta,time
from django.utils import timezone

today=timezone.localdate()
now = timezone.localtime()


from .models import Customer,LunchRecord,DinnerRecord
from Admin.models import AdminNotice

@login_required
def user_dashboard(request):
    user=request.user
    used_meals= user.total_meals - user.meal_balance
    cl_l=LunchRecord.objects.filter(service_choice="Cancel",customer=user).count()
    cl_d=DinnerRecord.objects.filter(service_choice="Cancel",customer=user).count()
    cancelled_meals=cl_l+cl_d

    lunch_record = LunchRecord.objects.filter(customer=user,for_date=today).first()
    dinner_record = DinnerRecord.objects.filter(customer=user,for_date=today).first()

    admin_notice=AdminNotice.objects.all()
    
    # tsunday= today.isoweekday() == 6  # for sunday use 6 
    tsunday= today.isoweekday() == 4  # use present date for testing puropose sunday to satur 0-7
    slunch_record = LunchRecord.objects.filter(customer=user,for_date= today  + timedelta(days=1)).first()

    # is_out_of_time_lunch = now.time() >= time(11, 0)
    # is_out_of_time_dinner = now.time() >= time(18, 0)
    # is_out_of_time_sundaylunch = now.time() >= time(23, 59)


    context={
        'user':user,
        'used_meals':used_meals,
        'cancelled_meals':cancelled_meals,
        'lunch_record':lunch_record,
        'dinner_record':dinner_record,
        'admin_notice':admin_notice,
        'tsunday':tsunday,
        'slunch_record':slunch_record,

        }
    return render(request, 'Customer/user-dashboard.html',context)


@login_required
def user_profile(request):
    user=request.user
    if request.method == "POST":
        default_lunch_service=request.POST.get("default_lunch_service")
        default_dinner_service=request.POST.get("default_dinner_service")
        status_availability=request.POST.get("status_availability")

        user.default_meal_choice="NONE"
        user.FLAGSHIP_MENU_LUNCH_default_choice="NONE"
        user.FLAGSHIP_MENU_DINNER_default_choice="NONE"
        user.PREMIUM_MENU_LUNCH_default_choice="NONE"
        user.PREMIUM_MENU_DINNER_default_choice="NONE"

        if user.subscription_choice == "NORMAL30" or user.subscription_choice == "NORMAL60" :            
            user.default_lunch_service_choice=default_lunch_service
            user.default_dinner_service_choice=default_dinner_service
            
            user.default_meal_choice=request.POST.get("default_meal_choice")
            
            user.user_status_active=True if status_availability == "True" else False
            user.save()

        if user.subscription_choice == "FLAGSHIP30" or user.subscription_choice == "FLAGSHIP60" :
            user.default_lunch_service_choice=default_lunch_service
            user.default_dinner_service_choice=default_dinner_service

            user.FLAGSHIP_MENU_LUNCH_default_choice=request.POST.get("default_flagship_lunch")
            user.FLAGSHIP_MENU_DINNER_default_choice=request.POST.get("default_flagship_dinner")
            
            user.user_status_active=True if status_availability == "True" else False

            user.save()
        
        if user.subscription_choice == "PREMIUM30" or user.subscription_choice == "PREMIUM60" :
            user.default_lunch_service_choice=default_lunch_service
            user.default_dinner_service_choice=default_dinner_service

            user.PREMIUM_MENU_LUNCH_default_choice=request.POST.get("default_premium_lunch")
            user.PREMIUM_MENU_DINNER_default_choice=request.POST.get("default_premium_dinner")
            
            user.user_status_active=True if status_availability == "True" else False

            user.save()

        return redirect("user_profile")
    return render(request,'Customer/user-profile.html')

@login_required
def user_lunch_form(request):
    if request.method != "POST":
        return redirect("user_dashboard")

    customer = request.user
    service_choice = request.POST.get("lunch_service")
    print(service_choice)
    meal_choice = None
    FLAGSHIP_choice = None
    PREMIUM_choice = None

    # Determine meal based on subscription
    if customer.subscription_choice in ("NORMAL30", "NORMAL60"):
        meal_choice = request.POST.get("meal_choice")

    elif customer.subscription_choice in ("FLAGSHIP30", "FLAGSHIP60"):
        FLAGSHIP_choice = request.POST.get("FLAGSHIP_choice")

    elif customer.subscription_choice in ("PREMIUM30", "PREMIUM60"):
        PREMIUM_choice = request.POST.get("PREMIUM_choice")

    with transaction.atomic():
        lr = LunchRecord.objects.create(
            customer=customer,
            for_date=today,
            meal_choice=meal_choice,
            FLAGSHIP_choice=FLAGSHIP_choice,
            PREMIUM_choice=PREMIUM_choice,
            meal_num_used=customer.meal_balance,
            service_choice=service_choice,
        )

        # Decrement meal balance only if service is not Cancel
        if service_choice != "Cancel":
            customer.meal_balance -= 1

            if customer.meal_balance <= 0:
                customer.meal_balance = 0
                customer.paused_subscription = True
                customer.user_status_active = False

            customer.save(update_fields=["meal_balance", "paused_subscription","user_status_active"])

            lr.decrement_done = True
            lr.save(update_fields=["decrement_done"])

    return redirect("user_dashboard")


@login_required
def user_sunday_lunch_form(request):
    if request.method != "POST":
        return redirect("user_dashboard")

    customer = request.user
    service_choice = request.POST.get("lunch_service")
    FLAGSHIP_choice = None
    PREMIUM_choice = None

    
    meal_choice = request.POST.get("meal_choice")


    with transaction.atomic():
        lr = LunchRecord.objects.create(
            customer=customer,
            for_date=today + timedelta(days=1),
            meal_choice=meal_choice,
            FLAGSHIP_choice=FLAGSHIP_choice,
            PREMIUM_choice=PREMIUM_choice,
            meal_num_used=customer.meal_balance,
            service_choice=service_choice,
        )

        # Decrement meal balance only if service is not Cancel
        if service_choice != "Cancel":
            customer.meal_balance -= 1

            if customer.meal_balance <= 0:
                customer.meal_balance = 0
                customer.paused_subscription = True
                customer.user_status_active = False

            customer.save(update_fields=["meal_balance", "paused_subscription","user_status_active"])

            lr.decrement_done = True
            lr.save(update_fields=["decrement_done"])

    return redirect("user_dashboard")





@login_required
def user_dinner_form(request):
    if request.method != "POST":
        return redirect("user_dashboard")

    customer = request.user
    service_choice = request.POST.get("dinner_service")

    meal_choice = None
    FLAGSHIP_choice = None
    PREMIUM_choice = None

    # Determine meal based on subscription
    if customer.subscription_choice in ("NORMAL30", "NORMAL60"):
        meal_choice = request.POST.get("meal_choice")

    elif customer.subscription_choice in ("FLAGSHIP30", "FLAGSHIP60"):
        FLAGSHIP_choice = request.POST.get("FLAGSHIP_choice")

    elif customer.subscription_choice in ("PREMIUM30", "PREMIUM60"):
        PREMIUM_choice = request.POST.get("PREMIUM_choice")

    with transaction.atomic():
        # Prevent duplicate dinner entry for the same day
        if DinnerRecord.objects.filter(customer=customer, for_date=today).exists():
            return redirect("user_dashboard")

        dr = DinnerRecord.objects.create(
            customer=customer,
            for_date=today,
            meal_choice=meal_choice,
            FLAGSHIP_choice=FLAGSHIP_choice,
            PREMIUM_choice=PREMIUM_choice,
            meal_num_used=customer.meal_balance,
            service_choice=service_choice,
        )

        # Decrement meal balance only if service is not Cancel
        if service_choice != "Cancel":
            customer.meal_balance -= 1

            if customer.meal_balance <= 0:
                customer.meal_balance = 0
                customer.paused_subscription = True
                customer.user_status_active = False

            customer.save(update_fields=["meal_balance", "paused_subscription","user_status_active"])

            dr.decrement_done = True
            dr.save(update_fields=["decrement_done"])

    return redirect("user_dashboard")
    
            
@login_required
def user_history(request):
    user = request.user

    # Order by date (latest first)
    lunch_records = LunchRecord.objects.filter(
        customer=user
    ).order_by("-for_date")

    dinner_records = DinnerRecord.objects.filter(
        customer=user
    ).order_by("-for_date")

    history = []

    # Add lunch records
    for record in lunch_records:
        history.append({
            "date": record.for_date,
            "meal_type": "Lunch",
            "service": record.service_choice,
            "status": "Cancelled" if record.service_choice == "Cancel" else "Completed",
            "meal_no": record.meal_num_used,
        })

    # Add dinner records
    for record in dinner_records:
        history.append({
            "date": record.for_date,
            "meal_type": "Dinner",
            "service": record.service_choice,
            "status": "Cancelled" if record.service_choice == "Cancel" else "Completed",
            "meal_no": record.meal_num_used,
        })

    context = {
        "history": history,
    }

    return render(request, "Customer/user-history.html", context)