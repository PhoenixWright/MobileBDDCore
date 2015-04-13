"""
tools to parse and extra additional data from behave contexts
"""
import re
import unicodedata


def slugify(dirty):
    """
    clean a string to make it suitable for filenames

    http://stackoverflow.com/a/7406369/3075814

    :param dirty: string to clean
    :type dirty: str

    :rtype: str
    """
    clean = unicodedata.normalize(u'NFKD', unicode(dirty)).encode(u'ascii', u'ignore')
    return re.sub(u'[^_,\-\d\w ]', u' ', clean).strip()


def gentrify_scenario_name(scenario):
    """
    outputs a readable scenario name that factors in whether or not the scenario
    was made from an outline with examples. if so, then it will include the data
    used as inputs. eg:
    my scenario, where x=1, y=2

    :type scenario: Scenario
    """
    return slugify(scenario.name)
