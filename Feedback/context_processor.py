def active_task(request):
    from Feedback.models import UserTask
    from UserManager.views import get_workbench_user
    if request.user.is_authenticated():
        w_user = get_workbench_user(request.user)
        active_task = UserTask.objects.filter(user=w_user, active=True, completed=False)
        if active_task.count() is not 0:
            return {'active_task': active_task[0].for_task}
    return {}

def check_if_active_task_complete(request):
    import re
    from Feedback.models import UserTask
    from UserManager.views import get_workbench_user
    if request.user.is_authenticated():
        w_user = get_workbench_user(request.user)
        active_task = UserTask.objects.filter(user=w_user, active=True, completed=False)
        if active_task.count() is not 0:
            active_task = active_task[0]
            end_point = active_task.for_task.end_point
            match = re.match(end_point, request.get_full_path())
            if match:
                active_task.completed = True
                active_task.save()
                return {'completed_task': active_task}
    return {}
