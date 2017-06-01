def workbench_user(request):
    from .models import WorkbenchUser
    import logging
    logger = logging.getLogger(__name__)
    if request.user.is_authenticated():
        logger.info('%s accessed the page %s', request.user, request.path)
        return {'workbench_user': WorkbenchUser.objects.get(user=request.user)}
    return {}
