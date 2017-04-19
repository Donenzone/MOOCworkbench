from build_manager.models import TravisInstance


class BuildWhatNowMixin(object):
    def what_to_do_now_ci(self):
        ci_message = "Enable Travis Builds on the Continuous Integration tab"
        ci_enabled = False
        ci_enabled_check = TravisInstance.objects.filter(experiment=self.experiment)
        if ci_enabled_check:
            ci_enabled = ci_enabled_check[0].enabled
        if not ci_enabled:
            return ci_message
        return "You've already enabled builds. Great!"
