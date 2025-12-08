import logging
from django.utils import timezone
from django.db.models import F
from django.db.models.functions import Greatest
from django.db import transaction
from django.http import JsonResponse

from Customers.models import Customer, LunchRecord, DinnerRecord

from django.shortcuts import render,redirect

logger = logging.getLogger(__name__)
CONSUMING_SERVICES = ("DineIn", "PickUp", "Delivery")


def gen_Lunch_record(request=None):
    """
    Create missing lunch records for active users and decrement balances exactly once
    for today's consuming records.
    """
    today = timezone.localdate()
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
                meal_choice=c.default_meal_choice,
                meal_num_used=c.meal_balance,
                service_choice=c.default_service_choice,
                FLAGSHIP_choice=c.FLAGSHIP_MENU_LUNCH_default_choice,
                PREMIUM_choice=c.PREMIUM_MENU_LUNCH_default_choice
            )
        )

    created_count = 0

    try:
        with transaction.atomic():
            if lunch_records_to_create:
                # ignore_conflicts avoids race-duplicate errors if another worker created same record.
                LunchRecord.objects.bulk_create(lunch_records_to_create, ignore_conflicts=True)
                # Count how many were inserted - best effort:
                created_count = len(lunch_records_to_create)

            # Decrement customers who have today's lunch record with a consuming service and haven't been decremented yet.
            customers_to_decrement = Customer.objects.filter(
                lunch_records__for_date=today,
                lunch_records__service_choice__in=CONSUMING_SERVICES,
                lunch_records__decrement_done=False
            ).distinct()

            # Decrement meal_balance but not below 0
            customers_to_decrement.update(meal_balance=Greatest(F("meal_balance") - 1, 0))

            # Mark related LunchRecord(s) as decremented
            LunchRecord.objects.filter(
                for_date=today,
                service_choice__in=CONSUMING_SERVICES,
                decrement_done=False
            ).update(decrement_done=True)

            # Update low-balance flags and active status
            Customer.objects.filter(meal_balance__lte=6).update(low_balance_status_active=True)
            # if balance <= 0 consider inactive
            Customer.objects.filter(meal_balance__lte=0).update(user_status_active=False)

    except Exception as e:
        logger.exception("Unexpected error in gen_Lunch_record: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"created_count": created_count})


def gen_Dinner_record(request=None):
    """
    Mirror of gen_Lunch_record for dinner.
    """
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
                meal_choice=c.default_meal_choice,
                meal_num_used=c.meal_balance,
                service_choice=c.default_service_choice,
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
                service_choice__in=CONSUMING_SERVICES,
                decrement_done=False
            ).update(decrement_done=True)

            Customer.objects.filter(meal_balance__lte=6).update(low_balance_status_active=True)
            Customer.objects.filter(meal_balance__lte=0).update(user_status_active=False)

    except Exception as e:
        logger.exception("Unexpected error in gen_Dinner_record: %s", e)
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"created_count": created_count})






# -------------------------------
# GLOBAL PLAN DICTIONARIES
# -------------------------------

PLAN_MAP = {
    "NORMAL30": "normal_1500",
    "NORMAL60": "normal_3000",
    "FLAGSHIP30": "flagship_1800",
    "FLAGSHIP60": "flagship_3400",
    "PREMIUM30": "premium_2200",
    "PREMIUM60": "premium_4200",
}

PLAN_MAP_DISPLAY = {
    "NORMAL30": "Normal (₹1500 — 30 meals)",
    "NORMAL60": "Normal (₹3000 — 60 meals)",
    "FLAGSHIP30": "Premium 1 (₹1800 — 30 meals)",
    "FLAGSHIP60": "Premium 1 (₹3400 — 60 meals)",
    "PREMIUM30": "Premium 2 (₹2200 — 30 meals)",
    "PREMIUM60": "Premium 2 (₹4200 — 60 meals)",
}

PLAN_TOTAL_MEALS = {
    "NORMAL30": 30,
    "NORMAL60": 60,
    "FLAGSHIP30": 30,
    "FLAGSHIP60": 60,
    "PREMIUM30": 30,
    "PREMIUM60": 60,
}

#-------------------------------------------------------
# Admin Dashboard section             
#-------------------------------------------------------
def admin_dashboard(request):
    today = timezone.localdate()

    print(today)
 
    # Fetch Today's Records
    lunch = LunchRecord.objects.filter(for_date=today)
    dinner = DinnerRecord.objects.filter(for_date=today)

    SERVICES = ["DineIn", "PickUp", "Delivery", "Cancel"]

    # --------------------------
    # INIT LUNCH DATA
    # --------------------------
    lunch_data = {
        serv: {
            "normal_1500": 0,
            "normal_3000": 0,
            "flagship_1800": 0,
            "flagship_3400": 0,
            "premium_2200": 0,
            "premium_4200": 0,
            "total": 0
        }
        for serv in SERVICES
    }

    # Fill lunch counts
    for rec in lunch:
        plan_key = PLAN_MAP.get(rec.customer.subscription_choice)
        serv = rec.service_choice
        lunch_data[serv][plan_key] += 1
        lunch_data[serv]["total"] += 1

    # Compute lunch totals row
    lunch_totals = {
        "normal_1500": 0,
        "normal_3000": 0,
        "flagship_1800": 0,
        "flagship_3400": 0,
        "premium_2200": 0,
        "premium_4200": 0,
        "total": 0
    }

    for serv in SERVICES:
        for col in lunch_totals:
            if col != "total":
                lunch_totals[col] += lunch_data[serv][col]

    lunch_totals["total"] = (
        lunch_totals["normal_1500"] +
        lunch_totals["normal_3000"] +
        lunch_totals["flagship_1800"] +
        lunch_totals["flagship_3400"] +
        lunch_totals["premium_2200"] +
        lunch_totals["premium_4200"]
    )

    # --------------------------
    # INIT DINNER DATA
    # --------------------------
    dinner_data = {
        serv: {
            "normal_1500": 0,
            "normal_3000": 0,
            "flagship_1800": 0,
            "flagship_3400": 0,
            "premium_2200": 0,
            "premium_4200": 0,
            "total": 0
        }
        for serv in SERVICES
    }

    # Fill dinner counts
    for rec in dinner:
        plan_key = PLAN_MAP.get(rec.customer.subscription_choice)
        serv = rec.service_choice
        dinner_data[serv][plan_key] += 1
        dinner_data[serv]["total"] += 1

    # Compute dinner totals row
    dinner_totals = {
        "normal_1500": 0,
        "normal_3000": 0,
        "flagship_1800": 0,
        "flagship_3400": 0,
        "premium_2200": 0,
        "premium_4200": 0,
        "total": 0
    }

    for serv in SERVICES:
        for col in dinner_totals:
            if col != "total":
                dinner_totals[col] += dinner_data[serv][col]

    dinner_totals["total"] = (
        dinner_totals["normal_1500"] +
        dinner_totals["normal_3000"] +
        dinner_totals["flagship_1800"] +
        dinner_totals["flagship_3400"] +
        dinner_totals["premium_2200"] +
        dinner_totals["premium_4200"]
    )

    # --------------------------
    # LOW BALANCE USERS
    # --------------------------
    low_balance_users = Customer.objects.filter(meal_balance__lt=6)
    low_balance_count = low_balance_users.count()

    # --------------------------
    # SEND TO TEMPLATE
    # --------------------------
    context = {
        "today": today,

        "lunch": lunch_data,
        "lunch_totals": lunch_totals,

        "dinner": dinner_data,
        "dinner_totals": dinner_totals,

        "low_balance_users": low_balance_users,
        "low_balance_count": low_balance_count,
    }

    return render(request, "Admin/admin-dashboard.html", context)




def service_list(request, meal, service):
    today = timezone.localdate()

    # meal = lunch or dinner
    if meal == "lunch":
        records = LunchRecord.objects.filter(for_date=today, service_choice=service)
    else:
        records = DinnerRecord.objects.filter(for_date=today, service_choice=service)

    # Attach final food choice dynamically
    final_records = []
    for r in records:
        sub = r.customer.subscription_choice
        
        # NORMAL plan → use meal_choice
        if sub in ["NORMAL30", "NORMAL60"]:
            food = r.meal_choice

        # FLAGSHIP plan → use flagship choice
        elif sub in ["FLAGSHIP30", "FLAGSHIP60"]:
            food = r.FLAGSHIP_choice

        # PREMIUM plan → use premium choice
        else:
            food = r.PREMIUM_choice

        # attach food choice to record
        r.final_food_choice = food
        final_records.append(r)

    context = {
        "meal": meal,
        "service": service,
        "records": final_records,
        "today": today,
    }

    return render(request, "Admin/service-list.html", context)


from Customers.models import (
    Customer,
    FLAGSHIP_MENU_LUNCH,
    FLAGSHIP_MENU_DINNER,
    PREMIUM_MENU_LUNCH,
    PREMIUM_MENU_DINNER,
)

def admin_user_management(request):
    if request.method == "POST":

        # ---------------- BASIC FIELDS ----------------
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        password = request.POST.get("password", "").strip()


        # ---------------- PLAN ----------------
        subscription_choice = request.POST.get("subscription_choice")
        total_meals = PLAN_TOTAL_MEALS.get(subscription_choice, 0)

        meal_used = int(request.POST.get("meal_used", 0))
        meal_balance = max(total_meals - meal_used, 0)

        # ---------------- DEFAULT SERVICE/MEAL ----------------
        default_service_choice = request.POST.get("default_service_choice")
        default_meal_choice = request.POST.get("default_meal_choice")

        # ---------------- MENU DEFAULTS ----------------
        flagship_lunch = request.POST.get("flagship_lunch_default", "NONE")
        flagship_dinner = request.POST.get("flagship_dinner_default", "NONE")
        premium_lunch = request.POST.get("premium_lunch_default", "NONE")
        premium_dinner = request.POST.get("premium_dinner_default", "NONE")

        # ---------------- PLAN ACCESS RULES ----------------
        thirty_plans = {"NORMAL30", "FLAGSHIP30", "PREMIUM30"}
        sixty_plans = {"NORMAL60", "FLAGSHIP60", "PREMIUM60"}

        if subscription_choice in thirty_plans:
            # admin selects one
            access_choice = request.POST.get("access_choice")
            if access_choice == "lunch":
                lunch_status = True
                dinner_status = False
            else:
                lunch_status = False
                dinner_status = True

        elif subscription_choice in sixty_plans:
            lunch_status = True
            dinner_status = True

        else:
            lunch_status = False
            dinner_status = False

        # ---------------- USER ACTIVE ----------------
        user_status = (request.POST.get("user_status_active") == "on")

        # ---------------- CREATE USER ----------------
        Customer.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            password=password,

            subscription_choice=subscription_choice,
            meal_balance=meal_balance,

            default_service_choice=default_service_choice,
            default_meal_choice=default_meal_choice,

            user_status_active=user_status,
            lunch_status_active=lunch_status,
            dinner_status_active=dinner_status,

            FLAGSHIP_MENU_LUNCH_default_choice=flagship_lunch,
            FLAGSHIP_MENU_DINNER_default_choice=flagship_dinner,
            PREMIUM_MENU_LUNCH_default_choice=premium_lunch,
            PREMIUM_MENU_DINNER_default_choice=premium_dinner,
        )

        return redirect("admin_user_management")

    # GET REQUEST: Send users + menu options
    users = Customer.objects.all().order_by("-id")

    context = {
        "users": users,
        "PLAN_MAP_DISPLAY": PLAN_MAP_DISPLAY,
        "PLAN_TOTAL_MEALS": PLAN_TOTAL_MEALS,

        "FLAGSHIP_MENU_LUNCH": FLAGSHIP_MENU_LUNCH,
        "FLAGSHIP_MENU_DINNER": FLAGSHIP_MENU_DINNER,
        "PREMIUM_MENU_LUNCH": PREMIUM_MENU_LUNCH,
        "PREMIUM_MENU_DINNER": PREMIUM_MENU_DINNER,
    }

    return render(request, "Admin/admin-user-management.html", context)




#---------------------------------------------------------------------------------------------------------------------------------


def daily_report(request):
    return render(request,"Admin/admin-daily-report.html")