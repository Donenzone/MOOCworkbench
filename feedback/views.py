from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from feedback.models import Feedback, Task, UserTask
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from user_manager.models import get_workbench_user
from django.db.models import Q
from django.shortcuts import reverse


@login_required
def set_task_active(request, task_id):
    task = Task.objects.get(id=task_id)
    w_user = get_workbench_user(request.user)
    existing_user_task = UserTask.objects.filter(active=True, for_task=task, user=w_user)
    if not existing_user_task:
        task_user = UserTask()
        task_user.for_task = task
        task_user.user = get_workbench_user(request.user)
        task_user.active = True
        task_user.save()
    return redirect(to=task.start_point)


class UserTaskListView(ListView):
    model = UserTask

    def get_context_data(self, **kwargs):
        context = super(UserTaskListView, self).get_context_data(**kwargs)
        context['tasks'] = Task.objects.filter(active=True)
        workbench_user = get_workbench_user(self.request.user)
        context['available_tasks'] = get_available_tasks(workbench_user)
        return context


def get_available_tasks(w_user):
    completed_and_active_tasks = [i.for_task for i in UserTask.objects.filter((Q(completed=True) | Q(active=True))).filter(user=w_user)]
    tasks = Task.objects.all()
    final_tasks = []
    for task in tasks:
        if not task in completed_and_active_tasks:
            dependency = task.dependent_on
            dependency_satisfied = UserTask.objects.filter(for_task=dependency, completed=True).count()
            if dependency_satisfied is not 0 or dependency.id is task.id:
                final_tasks.append(task)
    return final_tasks


class FeedbackCreateView(CreateView):
    model = Feedback
    fields = ['like', 'feedback_like', 'feedback_dislike', 'other_comments']

    def form_valid(self, form):
        if 'task_id' in self.kwargs:
            task = Task.objects.get(id=self.kwargs['task_id'])
            form.instance.for_task = task

            w_user = get_workbench_user(self.request.user)
            user_task = UserTask.objects.get(for_task=task, user=w_user, completed=True)
            user_task.left_feedback = True
            user_task.save()

        return super(FeedbackCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('task_list')
