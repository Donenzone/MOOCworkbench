import logging
import math

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from experiments_manager.models import Experiment
from feedback.views import get_available_tasks
from marketplace.models import (ExternalPackage, InternalPackage, Package,
                                PackageResource, PackageVersion)

from .forms import RegisterForm, WorkbenchUserForm
from .models import WorkbenchUser, get_workbench_user

logger = logging.getLogger(__name__)


@login_required
def index(request):
    workbench_user = WorkbenchUser.objects.get(user=request.user)
    experiments = Experiment.objects.filter(owner=workbench_user).order_by('-created')[:5]
    packages = InternalPackage.objects.filter(owner=workbench_user).order_by('-created')[:5]
    logger.info('%s accessed index', workbench_user)
    recent_versions = list(PackageVersion.objects.all().order_by('-created')[:5])
    recent_resources = list(PackageResource.objects.all().order_by('-created')[:5])
    recent_internal = list(InternalPackage.objects.all().order_by('-created')[:5])
    recent_external = list(ExternalPackage.objects.all().order_by('-created')[:5])
    recent_experiments = list(Experiment.objects.filter(public=True).order_by('created')[:5])
    total_list = recent_versions + recent_resources + recent_internal + recent_external + recent_experiments
    total_list = reversed(sorted(total_list, key=lambda x: x.created))
    return render(request, 'index.html', {'experiments': experiments,
                                          'packages': packages,
                                          'tasks': get_available_tasks(workbench_user),
                                          'activities': total_list})


class DetailProfileView(View):
    def get(self, request):
        workbench_user = get_workbench_user(request.user)
        return render(request, "user_manager/workbenchuser_detail.html", {'workbench_user': workbench_user})


class EditProfileView(View):
    def get(self, request):
        workbench_user = get_workbench_user(request.user)
        form = WorkbenchUserForm(instance=workbench_user)
        logger.info('%s edit get profile view', workbench_user)
        return render(request, "user_manager/workbenchuser_edit.html", {'form': form})

    def post(self, request):
        workbench_user = get_workbench_user(request.user)
        form = WorkbenchUserForm(request.POST, instance=workbench_user)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            user = workbench_user.user
            if current_password:
                if user.check_password(current_password) and change_password_of_user(workbench_user, form):
                    messages.add_message(request, messages.SUCCESS, 'Your password has been changed.')
                else:
                    messages.add_message(request, messages.ERROR, 'Passwords did not match '
                                                                  'or incorrect current password.')
                    return render(request, "user_manager/workbenchuser_edit.html", {'form': form})
            form.save()
            logger.info('%s edited profile successfully', workbench_user)
            return redirect(to='/')
        else:
            return render(request, "user_manager/workbenchuser_edit.html", {'form': form})


def change_password_of_user(w_user, form):
        new_password = form.cleaned_data['new_password']
        new_password_again = form.cleaned_data['new_password_again']
        if new_password == new_password_again:
            user = w_user.user
            user.set_password(new_password)
            user.save()
            return True
        return False


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
                logger.info('new user created: %s', workbench_user)
                return redirect(to='/')
            else:
                return render(request, 'user_manager/register.html', {'form': form})
        else:
            return render(request, 'user_manager/register.html', {'form': form})


def existing_user_check(email_address):
    return User.objects.filter(email=email_address)


class WorkbenchUserDetailView(View):
    def get(self, request, username):
        workbench_user = get_object_or_404(WorkbenchUser, user__username=username)
        recent_experiments = Experiment.objects.filter(owner=workbench_user, completed=True).order_by('-created')[:5]
        recent_packages = Package.objects.filter(owner=workbench_user).order_by('-created')[:5]
        return render(request, "user_manager/user_profile.html", {'w_user': workbench_user,
                                                                  'experiments': recent_experiments,
                                                                  'packages': recent_packages})


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
    users_query = WorkbenchUser.objects.filter(user__username=q)
    experiment_query = Experiment.objects.filter(Q(owner__user=user, title__contains=q) |
                                                 Q(completed=True, title__contains=q))
    return package_version_query, package_resource_query, internal_package_query, external_package_query, \
           experiment_query, users_query
