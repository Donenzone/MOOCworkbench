from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from UserManager.serializer import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import *
from django.views.generic.detail import DetailView
from django.utils import timezone
from ExperimentsManager.models import Experiment


class WorkbenchUserViewset(viewsets.ModelViewSet):
    queryset = WorkbenchUser.objects.all()
    serializer_class = WorkbenchUserSerializer


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@login_required
def index(request):
    workbench_user = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=workbench_user)[:5]
    return render(request, 'index.html', {'experiments': experiments})


def sign_in(request):
    if request.method == 'GET':
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect(to='/')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Incorrect username/password'})
        else:
            return render(request, 'login.html', {'form': form})


@login_required
def view_my_profile(request):
    workbench_user = WorkbenchUser.objects.get(user=request.user)
    return render(request, "UserManager/workbenchuser_detail.html", {'workbench_user': workbench_user})


@login_required
def edit_profile(request):
    workbench_user = WorkbenchUser.objects.get(user=request.user)
    if request.method == 'GET':
        form = WorkbenchUserForm(instance=workbench_user)
        return render(request, "UserManager/workbenchuser_edit.html", {'form': form})
    if request.method == 'POST':
        form = WorkbenchUserForm(request.POST, instance=workbench_user)
        if form.is_valid():
            form.save()
            return redirect(to='/')
        else:
            return render(request, "UserManager/workbenchuser_edit.html", {'form': form})


def sign_out(request):
    logout(request)
    return redirect(to='/')


def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'UserManager/register.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
            workbench_user = WorkbenchUser()
            workbench_user.netid = form.cleaned_data['netid']
            workbench_user.can_run_experiments = True
            workbench_user.user = user
            workbench_user.save()
            return redirect(to='/')
        else:
            return render(request, 'UserManager/register.html', {'form': form})
