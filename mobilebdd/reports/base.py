from behave.reporter.base import Reporter
from mobilebdd.behave_tools import gentrify_scenario_name


class BaseReporter(Reporter):
    """
    base reporter that will expand completed feature scenarios. this is done
    because behave doesnt expand scenario outlines into their own scenarios.
    """

    def __init__(self, config):
        super(BaseReporter, self).__init__(config)

        # it seems pycharm understands this way of documenting class instance
        # vars better than using the epydoc @ivar in the class doc.
        # ivar field: http://epydoc.sourceforge.net/manual-fields.html
        # ivar docstring: http://epydoc.sourceforge.net/manual-docstring.html
        # but both are valid epydocs. i would just prefer to put the doc in the
        # class doc, but whatever. life rolls on.
        self.features = []
        '''
        :ivar: list of completed features, with expanded scenario outlines
        :type: list[behave.model.Feature]
        '''

    def feature(self, feature):
        # if we have a scenario outline in a feature, we have to call 'walk'
        # because it wont be expanded. weird, but whatever.
        scenarios = []
        steps = 0
        for scenario in feature.walk_scenarios():
            scenario.name = gentrify_scenario_name(scenario)
            scenarios.append(scenario)
            for step in scenario.steps:
                step.id = steps
                steps += 1

        # change/update the scenarios field, because the one that was passed in
        # just has the un-expanded scenarios
        feature.scenarios = scenarios

        self.features.append(feature)
