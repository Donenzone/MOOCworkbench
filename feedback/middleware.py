class MiddlewareTaskCompleted(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import re
        from feedback.models import UserTask
        from user_manager.views import get_workbench_user
        from django.contrib import messages
        match = False
        if request.user.is_authenticated():
            w_user = get_workbench_user(request.user)
            active_task = UserTask.objects.filter(user=w_user, active=True, completed=False)
            if active_task:
                active_task = active_task[0]
                end_point = active_task.for_task.end_point
                match = re.match(end_point, request.get_full_path())
                if match:
                    active_task.completed = True
                    active_task.active = False
                    active_task.save()

        response = self.get_response(request)

        if match and active_task:
            messages.add_message(request, messages.INFO,
                                 'Great! You have completed the task {0}. '
                                 'Tell us about your experiences via Account / My Tasks'.
                                 format(active_task.for_task.name))

        return response
