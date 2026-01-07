import logging
from django.utils import timezone
from django.db.models import F
from django.db.models.functions import Greatest
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from Customers.models import Customer, LunchRecord, DinnerRecord, SERVICE_TYPE,SUBSCRIPTION_TYPE
from .models import AdminNotice,SubscriptionHistory
from django.shortcuts import render,redirect
from Customers.models import MEAL_MENU,FLAGSHIP_MENU_LUNCH,FLAGSHIP_MENU_DINNER,PREMIUM_MENU_LUNCH,PREMIUM_MENU_DINNER
from .backend_views import gen_Lunch_record,gen_Dinner_record,create_customer_history
today = timezone.localdate()
from datetime import date
from datetime import timedelta,time
from django.utils import timezone
now = timezone.localtime()
from django.contrib.auth import update_session_auth_hash


all_menus_lunch = list(dict.fromkeys(MEAL_MENU + FLAGSHIP_MENU_LUNCH + PREMIUM_MENU_LUNCH))
all_menus_dinner = list(dict.fromkeys(MEAL_MENU + FLAGSHIP_MENU_DINNER + PREMIUM_MENU_DINNER))
all_menus_sunday = list(dict.fromkeys(MEAL_MENU))


@staff_member_required(login_url='/login/')
def dashboard(request):
    customers = Customer.objects.filter(is_staff=False,is_superuser=False)
    lunch_record = LunchRecord.objects.filter(for_date=today)
    sunday_lunch_record = LunchRecord.objects.filter(for_date=today + timedelta(days=1),)
    dinner_record = DinnerRecord.objects.filter(for_date=today)
    admin_messgaes = AdminNotice.objects.all()
    tsunday= today.isoweekday() == 4

    menu_lunch_count = {}
    menu_sunday_count = {}
    menu_dinner_count = {}

    for key, _ in all_menus_lunch:
        menu_lunch_count[key] = 0

    for key, _ in all_menus_sunday:
        menu_sunday_count[key] = 0

    for key, _ in all_menus_dinner:
        menu_dinner_count[key] = 0

    for l in lunch_record:
        choice = l.meal_choice or l.FLAGSHIP_choice or l.PREMIUM_choice or l.sunday_choice
        # print(choice)
        if choice in menu_lunch_count:
            menu_lunch_count[choice] += 1

    for sl in sunday_lunch_record:
        choice = sl.sunday_choice
        # print(choice)
        if choice in menu_lunch_count:
            menu_sunday_count[choice] += 1

    for d in dinner_record:
        choice = d.meal_choice or d.FLAGSHIP_choice or d.PREMIUM_choice
        # print(choice)
        if choice in menu_dinner_count:
            menu_dinner_count[choice] += 1

    context={
        'total_customers':customers.count(),
        'total_inactive_customers':customers.filter(user_status_active=False,paused_subscription=False).count(),
        'total_plan_end_customers':customers.filter(paused_subscription=True,is_staff=False,is_superuser=False).count(),
        'tsunday':tsunday,

        'total_lunch':lunch_record.exclude(service_choice="Cancel").count(),
        'lunch_dinein':lunch_record.filter(service_choice="DineIn").count(),
        'lunch_delivery':lunch_record.filter(service_choice="Delivery").count(),
        'lunch_pickup':lunch_record.filter(service_choice="PickUp").count(),
        'lunch_cancelled':lunch_record.filter(service_choice="Cancel").count(),
        # 'lunch_inactive':customers.filter(lunch_status_active=True,user_status_active=False,paused_subscription=False).count(),
        'lunch_default_need':customers.filter(user_status_active=True,lunch_status_active=True).exclude(lunch_records__for_date=today).count(),
        
        'sunday_total_lunch':sunday_lunch_record.exclude(service_choice="Cancel").count(),
        'sunday_lunch_dinein':sunday_lunch_record.filter(service_choice="DineIn").count(),
        'sunday_lunch_delivery':sunday_lunch_record.filter(service_choice="Delivery").count(),
        'sunday_lunch_pickup':sunday_lunch_record.filter(service_choice="PickUp").count(),
        'sunday_lunch_cancelled':sunday_lunch_record.filter(service_choice="Cancel").count(),
        # 'sunday_lunch_inactive':customers.filter(lunch_status_active=True,user_status_active=False,paused_subscription=False).count(),
        'sunday_lunch_default_need':customers.filter(user_status_active=True,lunch_status_active=True).exclude(lunch_records__for_date=today + timedelta(days=1),).count(),

        'total_dinner':dinner_record.exclude(service_choice="Cancel").count(),
        'dinner_dinein':dinner_record.filter(service_choice="DineIn").count(),
        'dinner_delivery':dinner_record.filter(service_choice="Delivery").count(),
        'dinner_pickup':dinner_record.filter(service_choice="PickUp").count(),
        'dinner_cancelled':dinner_record.filter(service_choice="Cancel").count(),
        # 'dinner_inactive':customers.filter(dinner_status_active=True,user_status_active=False,paused_subscription=False).count(),
        'dinner_default_need':customers.filter(user_status_active=True,dinner_status_active=True).exclude(dinner_records__for_date=today).count(),

        "menu_lunch_count": menu_lunch_count,
        "menu_dinner_count": menu_dinner_count,
        "menu_sunday_count": menu_sunday_count,

        'low_balance_customer':customers.filter(meal_balance__lte=6),
        'admin_messgaes':admin_messgaes,
    }
    return render(request,"Admin/dashboard.html",context)



@staff_member_required(login_url='/login/')
def service_details(request, dayTime, service):
    if dayTime == "Lunch":
        if service=="Total":
            result = LunchRecord.objects.filter(for_date = today).exclude(service_choice="Cancel")
        elif service=="DE":
            result = Customer.objects.filter(user_status_active=True,lunch_status_active=True,is_staff=False).exclude(lunch_records__for_date=today)
        else:
            result = LunchRecord.objects.filter(for_date = today,service_choice=service)
    if dayTime == "Sunday Lunch":
        if service=="Total":
            result = LunchRecord.objects.filter(for_date=today + timedelta(days=1),).exclude(service_choice="Cancel")
        elif service=="DE":
            result = Customer.objects.filter(user_status_active=True,lunch_status_active=True,is_staff=False).exclude(lunch_records__for_date=today + timedelta(days=1))
        else:
            result = LunchRecord.objects.filter(for_date=today + timedelta(days=1),service_choice=service)

    if dayTime == "Dinner":
        if service=="Total":
            result = DinnerRecord.objects.filter(for_date = today).exclude(service_choice="Cancel")
        elif service=="DE":
            result = Customer.objects.filter(user_status_active=True,dinner_status_active=True,is_staff=False).exclude(dinner_records__for_date=today)
        else:
            result = DinnerRecord.objects.filter(for_date = today,service_choice=service)
    
    if service == "Cancel":
        cancelled_page=True
    else:
        cancelled_page=False
    
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
def customer_list(request,types):
    if types == "Inactive":
        result = Customer.objects.filter(is_staff=False,user_status_active=False,paused_subscription=False)
    if types == "PlanEnded":
        result = Customer.objects.filter(is_staff=False,paused_subscription=True)
    context = {
        "records": result,
        "types": types,
    }    
    return render(request,"Admin/customer-lists.html", context)

@staff_member_required(login_url='/login/')
def subscribers(request):
    CST=Customer.objects.filter(is_staff=False,is_superuser=False)
    N30=CST.filter(subscription_choice="NORMAL30")
    N60=CST.filter(subscription_choice="NORMAL60")
    F30=CST.filter(subscription_choice="FLAGSHIP30")
    F60=CST.filter(subscription_choice="FLAGSHIP60")
    P30=CST.filter(subscription_choice="PREMIUM30")
    P60=CST.filter(subscription_choice="PREMIUM60")
    context={
        "N30":N30,
        "N60":N60,
        "F30":F30,
        "F60":F60,
        "P30":P30,
        "P60":P60,
    }
    return render(request,"Admin/subscribers.html",context)

@staff_member_required(login_url='/login/')
def add_customer(request):
    if request.method == "POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        password=request.POST.get("password")
        address=request.POST.get("address")
        subscription_choice=request.POST.get("subscription_choice")
        meal_balance=request.POST.get("meal_balance")
        default_lunch_service_choice=request.POST.get("default_lunch_service_choice")
        default_dinner_service_choice=request.POST.get("default_dinner_service_choice")
        user_status_active = "user_status_active" in request.POST
        lunch_status_active = "lunch_status_active" in request.POST
        dinner_status_active = "dinner_status_active" in request.POST


        try:
            with transaction.atomic():
                user=Customer.objects.create_user(
                email=email,
                name=name,
                phone=phone,
                password=password,
                address=address,
                subscription_choice=subscription_choice,
                meal_balance=meal_balance,
                default_lunch_service_choice=default_lunch_service_choice,
                default_dinner_service_choice=default_dinner_service_choice,
                user_status_active=user_status_active,
                lunch_status_active=lunch_status_active,
                dinner_status_active=dinner_status_active,
                )
                user.save()
            return redirect("customer_profile", uid=user.id)
        except Exception as e:
            # logger.exception("Unexpected error in addind Customer : %s", e)
            return JsonResponse({"error": str(e)}, status=500)
    return render(request,"Admin/add-customer.html")




@staff_member_required(login_url="/login/")
def customer_profile(request, uid):
    user = get_object_or_404(Customer, pk=uid)

    def update_customer_from_post():
        user.name = request.POST.get("name", user.name)
        user.phone = request.POST.get("phone", user.phone)
        user.address = request.POST.get("address", user.address)
        user.email = request.POST.get("email", user.email)
        user.user_status_active = "user_status_active" in request.POST
        user.lunch_status_active = "lunch_status_active" in request.POST
        user.dinner_status_active = "dinner_status_active" in request.POST
        
        user.subscription_choice = request.POST.get(
            "subscription_choice", user.subscription_choice
        )
        user.default_sunday_choice = request.POST.get("default_sunday_choice")

        meal_balance = request.POST.get("meal_balance")
        
        if meal_balance is not None:
            user.meal_balance = int(meal_balance)

        password = request.POST.get("password")

        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)


        user.default_lunch_service_choice = request.POST.get(
            "default_lunch_service_choice", user.default_lunch_service_choice
        )
        user.default_dinner_service_choice = request.POST.get(
            "default_dinner_service_choice", user.default_dinner_service_choice
        )

    if request.method == "POST":
        action = request.POST.get("action")

        with transaction.atomic():

            if action == "renew":
                history = create_customer_history(user)
                if history == "created":
                    LunchRecord.objects.filter(customer=user).delete()
                    DinnerRecord.objects.filter(customer=user).delete()

                    user.subscription_phase += 1
                    user.paused_subscription = False
                    user.default_meal_choice = None
                    user.FLAGSHIP_MENU_LUNCH_default_choice = None
                    user.FLAGSHIP_MENU_DINNER_default_choice = None
                    user.PREMIUM_MENU_LUNCH_default_choice = None
                    user.PREMIUM_MENU_DINNER_default_choice = None

            if action in ("update", "renew"):
                update_customer_from_post()
                user.save()
                return redirect("customer_profile", uid=user.id)

    lunch_records = LunchRecord.objects.filter(
        customer=user
    ).order_by("-for_date")

    dinner_records = DinnerRecord.objects.filter(
        customer=user
    ).order_by("-for_date")

    history = []

    for record in lunch_records:
        history.append({
            "date": record.for_date,
            "meal_type": "Lunch",
            "service": record.service_choice,
            "meal_choice": record.meal_choice or record.FLAGSHIP_choice or record.PREMIUM_choice or record.sunday_choice or "UNKNOWN",  
            "meal_no": record.meal_num_used,
        })

    for record in dinner_records:
        history.append({
            "date": record.for_date,
            "meal_type": "Dinner",
            "service": record.service_choice,
            "meal_choice": record.meal_choice or record.FLAGSHIP_choice or record.PREMIUM_choice  or "UNKNOWN", 
            "meal_no": record.meal_num_used,
        })

    history.sort(key=lambda x: x["meal_no"])
    
    context = {
        "user": user,
        "subs_history":SubscriptionHistory.objects.filter(customer=user).order_by('subscription_phase'),
        "current_meal_history":history,
    }
    return render(request, "Admin/customer_profile.html", context)


@staff_member_required(login_url="/login/")
def meal_record(request):
    records = None
    meal_time = "Lunch"
    target_date = date.today()

    if request.method == "POST":
        meal_time = request.POST.get("meal_time", "Lunch")
        target_date = request.POST.get("target_date") or date.today()

        if meal_time == "Lunch":
            records = LunchRecord.objects.filter(for_date=target_date).exclude(service_choice="Cancel")
        elif meal_time == "Dinner":
            records = DinnerRecord.objects.filter(for_date=target_date).exclude(service_choice="Cancel")

    context = {
        "records": records,
        "selected_meal": meal_time,
        "selected_date": target_date,
    }
    return render(request, "Admin/meal-record.html", context)

@staff_member_required(login_url="/login/")
@require_POST
@transaction.atomic
def update_meal_record(request, selected_meal, ldid):
    service_choice = request.POST.get("service_choice")

    if selected_meal == "Lunch":
        record = get_object_or_404(LunchRecord, pk=ldid)
    elif selected_meal == "Dinner":
        record = get_object_or_404(DinnerRecord, pk=ldid)
    else:
        return redirect("meal_list")

    customer = record.customer

    if service_choice == "Cancel" and record.service_choice != "Cancel":
        customer.meal_balance += 1
        customer.save()

        record.meal_choice = None
        record.FLAGSHIP_choice = None
        record.PREMIUM_choice = None
        record.sunday_choice = None

    record.service_choice = service_choice

    if service_choice != "Cancel":
        if "sunday_choice" in request.POST:
            record.sunday_choice = request.POST.get("sunday_choice")

        elif "meal_choice" in request.POST:
            record.meal_choice = request.POST.get("meal_choice")

        elif "FLAGSHIP_choice" in request.POST:
            record.FLAGSHIP_choice = request.POST.get("FLAGSHIP_choice")

        elif "PREMIUM_choice" in request.POST:
            record.PREMIUM_choice = request.POST.get("PREMIUM_choice")

    record.save()
    return redirect("meal_record")

@staff_member_required(login_url="/login/")
def track_subscription(request):
    result=SubscriptionHistory.objects.all()
    context={
        'result':result,
        }
    return render(redirect,"Admin/track-subscription.html",context)

@staff_member_required(login_url="/login/")
def track_subscription_details(request,sid):
    result=get_object_or_404(SubscriptionHistory,pk=sid)
    l_count = sum(1 for meals in result.meal_history.values() if meals.get("lunch"))
    print(l_count)
    d_count = sum(1 for meals in result.meal_history.values() if meals.get("dinner"))
    context={
        'record':result,
        'l_count':l_count,
        'd_count':d_count,
        }
    return render(request,"Admin/subscription-datails.html",context)