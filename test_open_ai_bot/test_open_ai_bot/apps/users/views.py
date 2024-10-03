from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm

from .forms import NewUserForm
from django.shortcuts import render

def signUp(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:loginPage")
    else:
        form = NewUserForm()
    return render(request, "users/sign-up.html", {
        'form': form
    })

def loginPage(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("ChatViewer:homePage")
            else:
                return redirect("ChatViewer:homePage")
        else:
            return redirect("ChatViewer:homePage")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {
        'form': form
    })

def logoutUser(request):
    logout(request)
    return redirect("users:loginPage")
