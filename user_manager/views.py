from actstream.models import model_stream, action_object_stream

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse
from django.views.generic import View

from experiments_manager.models import Experiment
from feedback.views import get_available_tasks
from marketplace.models import ExternalPackage, InternalPackage, PackageVersion, PackageResource

from .models import get_workbench_user, WorkbenchUser
from .forms import WorkbenchUserForm, UserLoginForm
from .forms import RegisterForm


@login_required
def index(request):
    workbench_user = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=workbench_user)[:5]
    activity_stream = list(model_stream(PackageVersion)[:5])
    activity_stream += list(model_stream(ExternalPackage)[:5])
    activity_stream += list(model_stream(InternalPackage)[:5])
    activity_stream += list(model_stream(PackageResource)[:5])
    activity_stream += list(action_object_stream(workbench_user)[:5])
    return render(request, 'index.html', {'experiments': experiments,
                                          'tasks': get_available_tasks(workbench_user),
                                          'activity': activity_stream})


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


class DetailProfileView(View):
    def get(self, request):
        workbench_user = get_workbench_user(request.user)
        return render(request, "user_manager/workbenchuser_detail.html", {'workbench_user': workbench_user})


class EditProfileView(View):
    def get(self, request):
        workbench_user = get_workbench_user(request.user)
        form = WorkbenchUserForm(instance=workbench_user)
        return render(request, "user_manager/workbenchuser_edit.html", {'form': form})

    def post(self, request):
        workbench_user = get_workbench_user(request.user)
        form = WorkbenchUserForm(request.POST, instance=workbench_user)
        if form.is_valid():
            form.save()
            return redirect(to='/')
        else:
            return render(request, "user_manager/workbenchuser_edit.html", {'form': form})


def sign_out(request):
    logout(request)
    return redirect(to='/')


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'user_manager/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(self.request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['email']
            if not existing_user_check(new_email):
                user = User.objects.create_user(form.cleaned_data['username'],
                                                new_email,
                                                form.cleaned_data['password'])
                workbench_user = WorkbenchUser.objects.get(user=user)
                workbench_user.netid = form.cleaned_data['netid']
                workbench_user.save()
                return redirect(to='/')
            else:
                return render(request, 'user_manager/register.html', {'form': form})
        else:
            return render(request, 'user_manager/register.html', {'form': form})


def existing_user_check(email_address):
    return User.objects.filter(email=email_address)
