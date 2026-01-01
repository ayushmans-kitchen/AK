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

today = timezone.localdate()

logger = logging.getLogger(__name__)
CONSUMING_SERVICES = ("DineIn", "PickUp", "Delivery")



@staff_member_required(login_url='/login/')
def gen_Lunch_record(request=None):
    customers_no_record = Customer.objects.filter(
        user_status_active=True,
        lunch_status_active=True
    ).exclude(lunch_records__for_date=today)

    logger.debug("gen_Lunch_record: customers without record count=%d", customers_no_record.count())

    lunch_records_to_create = []
    for c in customers_no_record:
        logger.debug("creating lunch record for: %s", c.email)
        lunch_records_to_create.append(
            LunchRecord(
                customer=c,
                for_date=today,
                meal_num_used=c.meal_balance,
                service_choice=c.default_lunch_service_choice,
                meal_choice=c.default_meal_choice,
                FLAGSHIP_choice=c.FLAGSHIP_MENU_LUNCH_default_choice,
                PREMIUM_choice=c.PREMIUM_MENU_LUNCH_default_choice
            )
        )
    print(lunch_records_to_create)    
    created_count = 0

    try:
        with transaction.atomic():
            if lunch_records_to_create:
                LunchRecord.objects.bulk_create(lunch_records_to_create, ignore_conflicts=True)
                created_count = len(lunch_records_to_create)

            customers_to_decrement = Customer.objects.filter(
                lunch_records__for_date=today,
                lunch_records__service_choice__in=CONSUMING_SERVICES,
                lunch_records__decrement_done=False
            ).distinct()

            customers_to_decrement.update(meal_balance=Greatest(F("meal_balance") - 1, 0))

            LunchRecord.objects.filter(
                for_date=today,
                service_choice__in=("DineIn", "PickUp", "Delivery"),
                decrement_done=False
            ).update(decrement_done=True)

            Customer.objects.filter(meal_balance__lte=0).update(user_status_active=False,paused_subscription=True)

    except Exception as e:
        logger.exception("Unexpected error in gen_Lunch_record: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

    return redirect('ayushman_dashboard')


@staff_member_required(login_url='/login/')
def gen_Dinner_record(request=None):

    today = timezone.localdate()
    customers_no_record = Customer.objects.filter(
        user_status_active=True,
        dinner_status_active=True
    ).exclude(dinner_records__for_date=today)

    logger.debug("gen_Dinner_record: customers without record count=%d", customers_no_record.count())

    dinner_records_to_create = []
    for c in customers_no_record:
        logger.debug("creating dinner record for: %s", c.email)
        dinner_records_to_create.append(
            DinnerRecord(
                customer=c,
                for_date=today,
                meal_num_used=c.meal_balance,
                service_choice=c.default_dinner_service_choice,
                meal_choice=c.default_meal_choice,
                FLAGSHIP_choice=c.FLAGSHIP_MENU_DINNER_default_choice,
                PREMIUM_choice=c.PREMIUM_MENU_DINNER_default_choice
            )
        )

    created_count = 0

    try:
        with transaction.atomic():
            if dinner_records_to_create:
                DinnerRecord.objects.bulk_create(dinner_records_to_create, ignore_conflicts=True)
                created_count = len(dinner_records_to_create)

            customers_to_decrement = Customer.objects.filter(
                dinner_records__for_date=today,
                dinner_records__service_choice__in=CONSUMING_SERVICES,
                dinner_records__decrement_done=False
            ).distinct()

            customers_to_decrement.update(meal_balance=Greatest(F("meal_balance") - 1, 0))

            DinnerRecord.objects.filter(
                for_date=today,
                service_choice__in=("DineIn", "PickUp", "Delivery"),
                decrement_done=False
            ).update(decrement_done=True)

            Customer.objects.filter(meal_balance__lte=0).update(user_status_active=False,paused_subscription=True)

    except Exception as e:
        logger.exception("Unexpected error in gen_Dinner_record: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

    return redirect('ayushman_dashboard')


@staff_member_required(login_url='/login/')
def add_admin_message(request):
    message=request.POST.get("message")
    AdminNotice.objects.create(message=message)
    return redirect("ayushman_dashboard")

@staff_member_required(login_url='/login/')
def delete_admin_notice(request,mid):
    AdminNotice.objects.get(pk=mid).delete()
    return redirect("ayushman_dashboard")
    





def create_customer_history(customer):
    lunches = LunchRecord.objects.filter(customer=customer)
    dinners = DinnerRecord.objects.filter(customer=customer)

    history = {}

    for lr in lunches:
        date_key = str(lr.for_date)
        history.setdefault(date_key, {})

        history[date_key]["lunch"] = (
            "CANCELLED" if lr.service_choice == "Cancel"
            else lr.meal_choice or lr.FLAGSHIP_choice or lr.PREMIUM_choice or "UNKNOWN"
        )

    for dr in dinners:
        date_key = str(dr.for_date)
        history.setdefault(date_key, {})

        history[date_key]["dinner"] = (
            "CANCELLED" if dr.service_choice == "Cancel"
            else dr.meal_choice or dr.FLAGSHIP_choice or dr.PREMIUM_choice or "UNKNOWN"
        )

    SubscriptionHistory.objects.create(
        customer=customer,
        subscription_choice= customer.subscription_choice,
        subscription_phase= customer.subscription_phase,
        start_date= customer.date_joined,
        end_date= customer.profile_updated_at,
        meal_history= history,
    )

    return "created"
