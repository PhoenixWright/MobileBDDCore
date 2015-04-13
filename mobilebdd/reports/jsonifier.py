import json

from mobilebdd.reports.base import BaseReporter


class JsonReporter(BaseReporter):
    """
    outputs the test run results in the form of a json

    one example use case is to plug this into a bdd api that returns the results
    in json format.
    """

    def __init__(self, config):
        super(JsonReporter, self).__init__(config)

    def get_json(self):
        """
        :return: json payload of the test results
        :rtype: str
        """
        return json.dumps({u'features': self.features})
