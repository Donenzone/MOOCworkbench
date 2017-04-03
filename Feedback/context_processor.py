def active_task(request):
    from Feedback.models import UserTask
    from UserManager.views import get_workbench_user
    if request.user.is_authenticated():
        w_user = get_workbench_user(request.user)
        active_task = UserTask.objects.filter(user=w_user, active=True, completed=False)
        if active_task.count() is not 0:
            return {'active_task': active_task[0].for_task}
    return {}
