# spec for listener objects


class Listener(object):
    """
    a simple test listener for behave
    """
    def __init__(self):
        pass

    def before_all(self, context):
        """
        :type context: behave.runner.Context
        """
        pass

    def before_feature(self, feature):
        """
        :type feature: behave.model.Feature
        """
        pass

    def before_scenario(self, scenario):
        """
        :type scenario: behave.model.Scenario
        """
        pass

    def before_step(self, step):
        """
        :type step: behave.model.Step
        """
        pass

    def after_step(self, step):
        """
        :type step: behave.model.Step
        """
        pass

    def after_scenario(self, scenario):
        """
        :type scenario: behave.model.Scenario
        """
        pass

    def after_feature(self, feature):
        """
        :type feature: behave.model.Feature
        """
        pass

    def after_all(self, context):
        """
        :type context: behave.runner.Context
        """
        pass
