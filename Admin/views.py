import logging
from django.utils import timezone
from django.db.models import F
from django.db.models.functions import Greatest
from django.db import transaction
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from Customers.models import Customer, LunchRecord, DinnerRecord, SERVICE_TYPE,SUBSCRIPTION_TYPE

from django.shortcuts import render,redirect

today = timezone.localdate()




#----------------------------------------------------
# Admin Dashboard section             
#-------------------------------------------------------
@staff_member_required
def admin_dashboard(request):

    lunch = LunchRecord.objects.filter(for_date=today)
    dinner = DinnerRecord.objects.filter(for_date=today)

    SERVICES = ["DineIn", "PickUp", "Delivery", "Cancel"]

    LUNCH_REPORT = {'VEG': 0, 'NON_VEG': 0, 'PANEER': 0, 'MUSHROOM': 0,'CHICKEN': 0, 'EGG': 0, 'FISH': 0, 'PRAWN': 0, 'TOTAL_LUNCH': 0}
    DINNER_REPORT ={'VEG': 0, 'NON_VEG': 0, 'PANEER': 0, 'MUSHROOM': 0,'CHICKEN': 0, 'EGG': 0,  'FISH': 0, 'PRAWN': 0, 'TOTAL_DINNER': 0}

    for i in lunch:
        if i.meal_choice == "VEG" or i.FLAGSHIP_choice == "VEG"  or i.PREMIUM_choice=="VEG":
            LUNCH_REPORT['VEG'] += 1
        elif i.meal_choice == "NON-VEG" or i.FLAGSHIP_choice == "NON_VEG"  or i.PREMIUM_choice=="NON_VEG":
            LUNCH_REPORT['NON_VEG'] += 1
        elif i.FLAGSHIP_choice == "PANEER"  or i.PREMIUM_choice =="PANEER":
            LUNCH_REPORT['PANEER'] += 1
        elif i.FLAGSHIP_choice == "MUSHROOM"  or i.PREMIUM_choice =="MUSHROOM":
            LUNCH_REPORT['MUSHROOM'] += 1
        elif i.FLAGSHIP_choice == "CHICKEN"  or i.PREMIUM_choice=="CHICKEN":
            LUNCH_REPORT['CHICKEN'] += 1
        elif i.FLAGSHIP_choice == "EGG"  or i.PREMIUM_choice=="EGG":
            LUNCH_REPORT['EGG'] += 1
        elif i.FLAGSHIP_choice == "FISH"  or i.PREMIUM_choice=="FISH":
            LUNCH_REPORT['FISH'] += 1
        elif i.FLAGSHIP_choice == "PRAWN"  or i.PREMIUM_choice=="PRAWN":
            LUNCH_REPORT['PRAWN'] += 1

    LUNCH_REPORT["TOTAL_LUNCH"] = (LUNCH_REPORT["VEG"]+ LUNCH_REPORT["NON_VEG"]+ LUNCH_REPORT["PANEER"]+ LUNCH_REPORT["MUSHROOM"]+ LUNCH_REPORT["CHICKEN"]+ LUNCH_REPORT["EGG"]+ LUNCH_REPORT["FISH"]+ LUNCH_REPORT["PRAWN"])


    for i in dinner:
        if i.meal_choice == "VEG" or i.FLAGSHIP_choice == "VEG"  or i.PREMIUM_choice=="VEG":
            DINNER_REPORT['VEG'] += 1
        elif i.meal_choice == "NON-VEG" or i.FLAGSHIP_choice == "NON_VEG"  or i.PREMIUM_choice=="NON_VEG":
            DINNER_REPORT['NON_VEG'] += 1
        elif i.FLAGSHIP_choice == "PANEER"  or i.PREMIUM_choice=="PANEER":
            DINNER_REPORT['PANEER'] += 1
        elif i.FLAGSHIP_choice == "MUSHROOM"  or i.PREMIUM_choice=="MUSHROOM":
            DINNER_REPORT['MUSHROOM'] += 1
        elif i.FLAGSHIP_choice == "CHICKEN"  or i.PREMIUM_choice=="CHICKEN":
            DINNER_REPORT['CHICKEN'] += 1
        elif i.FLAGSHIP_choice == "EGG"  or i.PREMIUM_choice=="EGG":
            DINNER_REPORT['EGG'] += 1
        elif i.FLAGSHIP_choice == "FISH"  or i.PREMIUM_choice=="FISH":
            DINNER_REPORT['FISH'] += 1
        elif i.FLAGSHIP_choice == "PRAWN"  or i.PREMIUM_choice=="PRAWN":
            DINNER_REPORT['PRAWN'] += 1
    

    DINNER_REPORT["TOTAL_DINNER"] = (DINNER_REPORT["VEG"]+ DINNER_REPORT["NON_VEG"]+ DINNER_REPORT["PANEER"]+ DINNER_REPORT["MUSHROOM"]+ DINNER_REPORT["CHICKEN"]+ DINNER_REPORT["EGG"]+ DINNER_REPORT["FISH"]+ DINNER_REPORT["PRAWN"])



    lunch_counts = {
                    "DineIn": {
                        "NORMAL30": 0, "NORMAL60": 0,
                        "FLAGSHIP30": 0, "FLAGSHIP60": 0,
                        "PREMIUM30": 0, "PREMIUM60": 0,
                        "TOTAL": 0
                    },
                    "PickUp": {
                        "NORMAL30": 0, "NORMAL60": 0,
                        "FLAGSHIP30": 0, "FLAGSHIP60": 0,
                        "PREMIUM30": 0, "PREMIUM60": 0,
                        "TOTAL": 0
                    },
                    "Delivery": {
                        "NORMAL30": 0, "NORMAL60": 0,
                        "FLAGSHIP30": 0, "FLAGSHIP60": 0,
                        "PREMIUM30": 0, "PREMIUM60": 0,
                        "TOTAL": 0
                    },
                    "Cancel": {
                        "NORMAL30": 0, "NORMAL60": 0,
                        "FLAGSHIP30": 0, "FLAGSHIP60": 0,
                        "PREMIUM30": 0, "PREMIUM60": 0,
                        "TOTAL": 0
                    }
                }
    for record in lunch:
        service = record.service_choice
        plan = record.customer.subscription_choice
        lunch_counts[service][plan]+=1
        lunch_counts[service]["TOTAL"]+=1


    dinner_counts = {
                    "DineIn": {
                        "NORMAL30": 0, "NORMAL60": 0,
                        "FLAGSHIP30": 0, "FLAGSHIP60": 0,
                        "PREMIUM30": 0, "PREMIUM60": 0,
                        "TOTAL": 0
                    },
                    "PickUp": {
                        "NORMAL30": 0, "NORMAL60": 0,
                        "FLAGSHIP30": 0, "FLAGSHIP60": 0,
                        "PREMIUM30": 0, "PREMIUM60": 0,
                        "TOTAL": 0
                    },
                    "Delivery": {
                        "NORMAL30": 0, "NORMAL60": 0,
                        "FLAGSHIP30": 0, "FLAGSHIP60": 0,
                        "PREMIUM30": 0, "PREMIUM60": 0,
                        "TOTAL": 0
                    },
                    "Cancel": {
                        "NORMAL30": 0, "NORMAL60": 0,
                        "FLAGSHIP30": 0, "FLAGSHIP60": 0,
                        "PREMIUM30": 0, "PREMIUM60": 0,
                        "TOTAL": 0
                    }
                }
    for record in dinner:
        service = record.service_choice
        plan = record.customer.subscription_choice
        dinner_counts[service]["TOTAL"]+=1
        dinner_counts[service][plan]+=1





    low_balance_users = Customer.objects.filter(
        meal_balance__lt=6,
        user_status_active=True
        ).order_by("meal_balance")

    low_balance_count = low_balance_users.count()

    
    context = {
        "lunch":lunch,
        "dinner":dinner,
        "LUNCH_REPORT":LUNCH_REPORT,
        "DINNER_REPORT":DINNER_REPORT,
        "lunch_counts": lunch_counts,
        "dinner_counts":dinner_counts,
        "low_balance_users":low_balance_users,
        "low_balance_count":low_balance_count,
        
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
        food=(r.meal_choice or r.FLAGSHIP_choice or r.PREMIUM_choice or "UNKNOWN")
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

# def admin_user_management(request):
#     if request.method == "POST":

#         # ---------------- BASIC FIELDS ----------------
#         name = request.POST.get("name", "").strip()
#         email = request.POST.get("email", "").strip()
#         phone = request.POST.get("phone", "").strip()
#         address = request.POST.get("address", "").strip()
#         password = request.POST.get("password", "").strip()


#         # ---------------- PLAN ----------------
#         subscription_choice = request.POST.get("subscription_choice")
#         total_meals = PLAN_TOTAL_MEALS.get(subscription_choice, 0)

#         meal_used = int(request.POST.get("meal_used", 0))
#         meal_balance = max(total_meals - meal_used, 0)

#         # ---------------- DEFAULT SERVICE/MEAL ----------------
#         default_service_choice = request.POST.get("default_service_choice")
#         default_meal_choice = request.POST.get("default_meal_choice")

#         # ---------------- MENU DEFAULTS ----------------
#         flagship_lunch = request.POST.get("flagship_lunch_default", "NONE")
#         flagship_dinner = request.POST.get("flagship_dinner_default", "NONE")
#         premium_lunch = request.POST.get("premium_lunch_default", "NONE")
#         premium_dinner = request.POST.get("premium_dinner_default", "NONE")

#         # ---------------- PLAN ACCESS RULES ----------------
#         thirty_plans = {"NORMAL30", "FLAGSHIP30", "PREMIUM30"}
#         sixty_plans = {"NORMAL60", "FLAGSHIP60", "PREMIUM60"}

#         if subscription_choice in thirty_plans:
#             # admin selects one
#             access_choice = request.POST.get("access_choice")
#             if access_choice == "lunch":
#                 lunch_status = True
#                 dinner_status = False
#             else:
#                 lunch_status = False
#                 dinner_status = True

#         elif subscription_choice in sixty_plans:
#             lunch_status = True
#             dinner_status = True

#         else:
#             lunch_status = False
#             dinner_status = False

#         # ---------------- USER ACTIVE ----------------
#         user_status = (request.POST.get("user_status_active") == "on")

#         # ---------------- CREATE USER ----------------
#         Customer.objects.create(
#             name=name,
#             email=email,
#             phone=phone,
#             address=address,
#             password=password,

#             subscription_choice=subscription_choice,
#             meal_balance=meal_balance,

#             default_service_choice=default_service_choice,
#             default_meal_choice=default_meal_choice,

#             user_status_active=user_status,
#             lunch_status_active=lunch_status,
#             dinner_status_active=dinner_status,

#             FLAGSHIP_MENU_LUNCH_default_choice=flagship_lunch,
#             FLAGSHIP_MENU_DINNER_default_choice=flagship_dinner,
#             PREMIUM_MENU_LUNCH_default_choice=premium_lunch,
#             PREMIUM_MENU_DINNER_default_choice=premium_dinner,
#         )

#         return redirect("admin_user_management")

#     # GET REQUEST: Send users + menu options
#     users = Customer.objects.all().order_by("-id")

#     context = {
#         "users": users,
#         "PLAN_MAP_DISPLAY": PLAN_MAP_DISPLAY,
#         "PLAN_TOTAL_MEALS": PLAN_TOTAL_MEALS,

#         "FLAGSHIP_MENU_LUNCH": FLAGSHIP_MENU_LUNCH,
#         "FLAGSHIP_MENU_DINNER": FLAGSHIP_MENU_DINNER,
#         "PREMIUM_MENU_LUNCH": PREMIUM_MENU_LUNCH,
#         "PREMIUM_MENU_DINNER": PREMIUM_MENU_DINNER,
#     }

#     return render(request, "Admin/admin-user-management.html", context)




#----------------------------------------------------------------------------------------------------------------------


def daily_report(request):
    today = timezone.localdate()
    users = Customer.objects.all().order_by("-id")
    lunch_records = LunchRecord.objects.filter(for_date=today)
    dinner_records = DinnerRecord.objects.filter(for_date=today)


    

    context = {
        "today": today,
        "users": users,
        "lunch_records": lunch_records,
        "dinner_records":dinner_records,
    }
    return render(request, "Admin/admin-daily-report.html", context)




def complete_report(request):
    return render(request,"Admin/admin-complete-report.html")





#=================================syarted new admin============================================================================

@staff_member_required(login_url='/login/')
def dashboard(request):
    return render(request,"Admin/dashboard.html")
    

@staff_member_required(login_url='/login/')
def subscribers(request):
    return render(request,"Admin/subscribers.html")


@staff_member_required(login_url='/login/')
def profile(request):
    return render(request,"Admin/profile.html")

