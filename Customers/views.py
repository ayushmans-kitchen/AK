from django.shortcuts import render

def user_dashboard(request):
    return render(request,"Customer/user-dashboard.html")


def user_history(request):
    return render(request,"Customer/user-history.html")