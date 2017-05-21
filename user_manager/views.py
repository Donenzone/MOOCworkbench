import logging
import math

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
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
        q = request.GET.get('q')
        page = request.GET.get('page')
        page = int(page) if page is not None else 1
        results, nr_of_pages = get_search_results(request.user, q, page)
        return render(request, 'search.html', {'results': results, 'query': q, 'page': page,
                                               'next_page': page + 1,
                                               'previous_page': page - 1,
                                               'nr_of_pages': nr_of_pages,
                                               'nr_of_pages_range': range(1, nr_of_pages+1)})
    return render(request, 'search.html', {})


def get_search_results(user, q, page_nr=1, page_size=25):
    start_value = (page_nr - 1) * page_size
    end_value = start_value + page_size
    search_query_list = build_search_queries(q, user)
    total_count = sum([x.count() for x in search_query_list])
    nr_of_pages = int(math.ceil(total_count / page_size))
    total_list = [list(x.order_by('-created')[start_value:end_value]) for x in search_query_list]
    total_flat_list = [item for sublist in total_list for item in sublist]
    total_flat_list = sorted(total_flat_list, key=lambda x: x.created)
    return total_flat_list, nr_of_pages


def build_search_queries(q, user):
    package_version_query = PackageVersion.objects.filter(version_nr__contains=q)
    package_resource_query = PackageResource.objects.filter(title__contains=q)
    internal_package_query = InternalPackage.objects.filter(name__contains=q)
    external_package_query = ExternalPackage.objects.filter(name__contains=q)
    experiment_query = Experiment.objects.filter(Q(owner__user=user, title__contains=q) |
                                                 Q(completed=True, title__contains=q))
    return package_version_query, package_resource_query, internal_package_query, external_package_query, \
           experiment_query
