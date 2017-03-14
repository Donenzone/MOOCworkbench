def workbench_user(request):
    from .models import WorkbenchUser
    if request.user.is_authenticated():
        return {'workbench_user': WorkbenchUser.objects.get(user=request.user)}
