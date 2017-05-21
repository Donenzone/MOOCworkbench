import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.generic import View

from experiments_manager.models import Experiment
from feedback.views import get_available_tasks
from marketplace.models import PackageVersion, PackageResource, InternalPackage, ExternalPackage

from .models import get_workbench_user, WorkbenchUser
from .forms import WorkbenchUserForm, UserLoginForm
from .forms import RegisterForm


logger = logging.getLogger(__name__)


@login_required
def index(request):
    workbench_user = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=workbench_user).order_by('-created')[:5]
    logger.debug('%s accessed index', workbench_user)
    recent_versions = list(PackageVersion.objects.all().order_by('-created')[:5])
    recent_resources = list(PackageResource.objects.all().order_by('-created')[:5])
    recent_internal = list(InternalPackage.objects.all().order_by('-created')[:5])
    recent_external = list(ExternalPackage.objects.all().order_by('-created')[:5])
    total_list = recent_versions + recent_resources + recent_internal + recent_external
    total_list = sorted(total_list, key=lambda x: x.created)
    return render(request, 'index.html', {'experiments': experiments,
                                          'tasks': get_available_tasks(workbench_user),
                                          'activities': total_list})


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
                logger.debug('%s signed in successfully', user)
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
        logger.debug('%s edit get profile view', workbench_user)
        return render(request, "user_manager/workbenchuser_edit.html", {'form': form})

    def post(self, request):
        workbench_user = get_workbench_user(request.user)
        form = WorkbenchUserForm(request.POST, instance=workbench_user)
        if form.is_valid():
            form.save()
            logger.debug('%s edited profile successfully', workbench_user)
            return redirect(to='/')
        else:
            return render(request, "user_manager/workbenchuser_edit.html", {'form': form})


def sign_out(request):
    logger.debug('%s user about to sign out', request.user)
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
                logger.debug('new user created: %s', workbench_user)
                return redirect(to='/')
            else:
                return render(request, 'user_manager/register.html', {'form': form})
        else:
            return render(request, 'user_manager/register.html', {'form': form})


def existing_user_check(email_address):
    return User.objects.filter(email=email_address)


@login_required
def search(request):
    if 'q' in request.GET:
        q = request.GET['q']
        recent_versions = list(PackageVersion.objects.filter(version_nr__contains=q).order_by('-created')[:5])
        recent_resources = list(PackageResource.objects.filter(title__contains=q).order_by('-created')[:5])
        recent_internal = list(InternalPackage.objects.filter(name__contains=q).order_by('-created')[:5])
        recent_external = list(ExternalPackage.objects.filter(name__contains=q).order_by('-created')[:5])
        total_list = recent_versions + recent_resources + recent_internal + recent_external
        total_list = sorted(total_list, key=lambda x: x.created)
        return render(request, 'search.html', {'results': total_list, 'query': q})
    return render(request, 'search.html', {})
