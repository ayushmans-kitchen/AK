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

#=================================syarted new admin============================================================================

@staff_member_required(login_url='/login/')
def dashboard(request):
    return render(request,"Admin/dashboard.html")

@staff_member_required(login_url='/login/')
def service_details(request):
    return render(request,"Admin/service-details.html")
    

@staff_member_required(login_url='/login/')
def subscribers(request):
    return render(request,"Admin/subscribers.html")


@staff_member_required(login_url='/login/')
def profile(request):
    return render(request,"Admin/profile.html")

