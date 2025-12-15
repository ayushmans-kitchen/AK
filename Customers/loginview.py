from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)
        print(password)
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "Customer/login.html")

def logout_view(request):
    logout(request)
    return redirect('login')
