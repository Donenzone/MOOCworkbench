def active_task(request):
    from feedback.models import UserTask
    from user_manager.views import get_workbench_user
    if request.user.is_authenticated():
        w_user = get_workbench_user(request.user)
        active_task = UserTask.objects.filter(user=w_user, active=True, completed=False)
        if active_task:
            return {'active_task': active_task[0].for_task}
    return {}
