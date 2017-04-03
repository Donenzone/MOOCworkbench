from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Feedback.models import Feedback, Task, UserTask
from UserManager.models import get_workbench_user

@login_required
def set_task_active(request, task_id):
    task = Task.objects.get(id=task_id)
    w_user = get_workbench_user(request.user)
    existing_user_task = UserTask.objects.filter(active=True, for_task=task, user=w_user)
    if existing_user_task.count() is 0:
        task_user = UserTask()
        task_user.for_task = task
        task_user.user = get_workbench_user(request.user)
        task_user.active = True
        task_user.save()
    return redirect(to=task.start_point)
