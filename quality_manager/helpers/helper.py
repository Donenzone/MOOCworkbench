from quality_manager.models import ExperimentMeasureResult


class ScoreCard(object):
    def __init__(self, experiment, for_step=None):
        self.experiment = experiment
        if for_step:
            self.step = for_step
        else:
            self.step = self.experiment.get_active_step()

    def caculate_score(self):
        pass


def scorecard_for_step(experiment, for_step):
    pass