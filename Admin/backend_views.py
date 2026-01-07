import logging
from django.utils import timezone
from django.db.models import F
from django.db.models.functions import Greatest
from django.db import transaction
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from Customers.models import Customer, LunchRecord, DinnerRecord

from .models import SubscriptionHistory,AdminNotice
from django.shortcuts import render,redirect
from datetime import timedelta,time
from django.utils import timezone

today=timezone.localdate()
now = timezone.localtime()
today = timezone.localdate()

logger = logging.getLogger(__name__)
CONSUMING_SERVICES = ("DineIn", "PickUp", "Delivery")



@staff_member_required(login_url="/login/")
def gen_Lunch_record(request):
    today = timezone.localdate()

    customers_no_record = Customer.objects.filter(
        user_status_active=True,
        lunch_status_active=True,
        meal_balance__gt=0
    ).exclude(lunch_records__for_date=today)

    lunch_records = [
        LunchRecord(
            customer=c,
            for_date=today,
            meal_num_used=c.meal_balance,
            service_choice=c.default_lunch_service_choice,
            sunday_choice=None,
            meal_choice=(
                c.default_meal_choice
                if c.subscription_choice in ["NORMAL30", "NORMAL60"]
                else None
            ),

            FLAGSHIP_choice=(
                c.FLAGSHIP_MENU_LUNCH_default_choice
                if c.subscription_choice in ["FLAGSHIP30", "FLAGSHIP60"]
                else None
            ),

            PREMIUM_choice=(
                c.PREMIUM_MENU_LUNCH_default_choice
                if c.subscription_choice in ["PREMIUM30", "PREMIUM60"]
                else None
            ),
        )
        for c in customers_no_record
    ]

    try:
        with transaction.atomic():
            LunchRecord.objects.bulk_create(lunch_records, ignore_conflicts=True)

            consuming_records = LunchRecord.objects.filter(
                for_date=today,
                service_choice__in=CONSUMING_SERVICES,
                decrement_done=False
            )

            customer_ids = consuming_records.values_list("customer_id", flat=True)

            Customer.objects.filter(id__in=customer_ids).update(
                meal_balance=Greatest(F("meal_balance") - 1, 0)
            )

            consuming_records.update(decrement_done=True)

            Customer.objects.filter(meal_balance__lte=0).update(
                user_status_active=False,
                paused_subscription=True
            )

    except Exception as e:
        logger.exception("Lunch generation failed: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

    return redirect("ayushman_dashboard")

@staff_member_required(login_url="/login/")
def gen_sunday_record(request):
    today = timezone.localdate()
    sunday = today + timedelta(days=1)

    customers_no_record = Customer.objects.filter(
        user_status_active=True,
        lunch_status_active=True,
        meal_balance__gt=0
    ).exclude(lunch_records__for_date=sunday)

    lunch_records = [
        LunchRecord(
            customer=c,
            for_date=sunday,
            meal_num_used=c.meal_balance,
            service_choice=c.default_lunch_service_choice,

            sunday_choice=c.default_sunday_choice,
            meal_choice=None,
            FLAGSHIP_choice=None,
            PREMIUM_choice=None,
        )
        for c in customers_no_record
    ]

    try:
        with transaction.atomic():
            LunchRecord.objects.bulk_create(lunch_records, ignore_conflicts=True)

            consuming_records = LunchRecord.objects.filter(
                for_date=sunday,
                service_choice__in=CONSUMING_SERVICES,
                decrement_done=False
            )

            customer_ids = consuming_records.values_list("customer_id", flat=True)

            Customer.objects.filter(id__in=customer_ids).update(
                meal_balance=Greatest(F("meal_balance") - 1, 0)
            )

            consuming_records.update(decrement_done=True)

            Customer.objects.filter(meal_balance__lte=0).update(
                user_status_active=False,
                paused_subscription=True
            )

    except Exception as e:
        logger.exception("Sunday lunch generation failed: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

    return redirect("ayushman_dashboard")
@staff_member_required(login_url="/login/")
def gen_Dinner_record(request):
    today = timezone.localdate()

    customers_no_record = Customer.objects.filter(
        user_status_active=True,
        dinner_status_active=True,
        meal_balance__gt=0
    ).exclude(dinner_records__for_date=today)

    dinner_records = [
        DinnerRecord(
            customer=c,
            for_date=today,
            meal_num_used=c.meal_balance,
            service_choice=c.default_dinner_service_choice,
            meal_choice=(
                c.default_meal_choice
                if c.subscription_choice in ["NORMAL30", "NORMAL60"]
                else None
            ),

            FLAGSHIP_choice=(
                c.FLAGSHIP_MENU_DINNER_default_choice
                if c.subscription_choice in ["FLAGSHIP30", "FLAGSHIP60"]
                else None
            ),

            PREMIUM_choice=(
                c.PREMIUM_MENU_DINNER_default_choice
                if c.subscription_choice in ["PREMIUM30", "PREMIUM60"]
                else None
            ),
        )
        for c in customers_no_record
    ]

    try:
        with transaction.atomic():
            DinnerRecord.objects.bulk_create(dinner_records, ignore_conflicts=True)

            consuming_records = DinnerRecord.objects.filter(
                for_date=today,
                service_choice__in=CONSUMING_SERVICES,
                decrement_done=False
            )

            customer_ids = consuming_records.values_list("customer_id", flat=True)

            Customer.objects.filter(id__in=customer_ids).update(
                meal_balance=Greatest(F("meal_balance") - 1, 0)
            )

            consuming_records.update(decrement_done=True)

            Customer.objects.filter(meal_balance__lte=0).update(
                user_status_active=False,
                paused_subscription=True
            )

    except Exception as e:
        logger.exception("Dinner generation failed: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

    return redirect("ayushman_dashboard")



@staff_member_required(login_url='/login/')
def add_admin_message(request):
    message=request.POST.get("message")
    AdminNotice.objects.create(message=message)
    return redirect("ayushman_dashboard")

@staff_member_required(login_url='/login/')
def delete_admin_notice(request,mid):
    AdminNotice.objects.get(pk=mid).delete()
    return redirect("ayushman_dashboard")
    

from django.db.models import Min

def create_customer_history(customer):
    lunches = LunchRecord.objects.filter(customer=customer)
    dinners = DinnerRecord.objects.filter(customer=customer)

    history = {}

    for lr in lunches:
        date_key = str(lr.for_date)
        history.setdefault(date_key, {})

        history[date_key]["lunch"] = {
            "meal_num_used": lr.meal_num_used,
            "service_choice": lr.service_choice,
            "food_choice": lr.meal_choice or lr.FLAGSHIP_choice or lr.PREMIUM_choice or lr.sunday_choice or "UNKNOWN",
        }

    for dr in dinners:
        date_key = str(dr.for_date)
        history.setdefault(date_key, {})

        history[date_key]["dinner"] = {
            "meal_num_used": dr.meal_num_used,
            "service_choice": dr.service_choice,
            "food_choice": dr.meal_choice or lr.FLAGSHIP_choice or lr.PREMIUM_choice or  "UNKNOWN",
        }

    lunch_start = lunches.aggregate(Min("for_date"))["for_date__min"]
    dinner_start = dinners.aggregate(Min("for_date"))["for_date__min"]

    dates = [d for d in (lunch_start, dinner_start) if d is not None]
    start_date = min(dates) if dates else customer.profile_updated_at


    SubscriptionHistory.objects.create(
        customer=customer,
        subscription_choice=customer.subscription_choice,
        subscription_phase=customer.subscription_phase,
        start_date=start_date,
        end_date=customer.profile_updated_at,
        meal_history=history,
    )

    return "created"

