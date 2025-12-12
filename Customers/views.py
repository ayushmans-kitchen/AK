from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db import transaction
import json

from django.utils import timezone
today=timezone.localdate()


from .models import Customer,LunchRecord,DinnerRecord

@login_required
def user_dashboard(request):
    user=request.user
    used_meals= user.total_meals - user.meal_balance
    print(used_meals)
    print(user.total_meals)
    print(user.meal_balance)
    cl_l=LunchRecord.objects.filter(service_choice="Cancel",customer=user).count()
    cl_d=DinnerRecord.objects.filter(service_choice="Cancel",customer=user).count()
    cancelled_meals=cl_l+cl_d

    lunch_record = LunchRecord.objects.filter(customer=user,for_date=today).first()
    dinner_record = DinnerRecord.objects.filter(customer=user,for_date=today).first()

    context={
        'user':user,
        'used_meals':used_meals,
        'cancelled_meals':cancelled_meals,
        'lunch_record':lunch_record,
        'dinner_record':dinner_record,
        }
    return render(request, 'Customer/user-dashboard.html',context)




@login_required
def user_lunch_form(request):
    if request.method != "POST":
        return redirect("user_dashboard")

    customer = request.user
    service_choice = request.POST.get("lunch_service")

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

        
            

def user_history(request):
    return render(request,"Customer/user-history.html")