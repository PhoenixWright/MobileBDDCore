"""
steps that modify or retrieve device states
"""

# noinspection PyUnresolvedReferences
from behave import *
import time
import logging


log = logging.getLogger(u'mobilebdd')


@step(u'I rotate the device to {rotation}')
@step(u'I rotate to {rotation}')
def _step(context, rotation):
    """
    :type context: HackedContext
    """
    log.debug(u'rotating to {}'.format(rotation))

    rotation = rotation.strip().upper()
    assert rotation in (u'PORTRAIT', u'LANDSCAPE'), u'invalid rotation: ' + rotation

    current_context = context.driver.context

    if current_context != u'NATIVE_APP':
        context.driver.switch_to.context(u'NATIVE_APP')

    context.driver.orientation = rotation

    if context.driver.current_context != current_context:
        context.driver.switch_to.context(current_context)

    log.debug(u'rotated. sleeping to let device settle')

    # wait a little bit so phone can finish rendering the new content
    # this will make sure rotated screenshots look right
    time.sleep(2)

    log.debug(u'rotate step done')


@step(u'current activity should be {activity}')
@step(u'the current activity should be {activity}')
def _step(context, activity):
    """
    :type context: HackedContext
    """

    assert context.driver.current_activity.strip().lower().endswith(activity.strip().lower()),\
        u'Expected activity to be {} but instead it was {}'.format(activity, context.driver.current_activity)

@step(u'I clear the {log_name} logs')
def _step(context, log_name):
    """
    Clears the logcat for this scenario. This is a temporary clear and only applies for this scenario, so messages cleared
    by this step may appear in a later scenario. For best results, use this at the very beginning of a scenario that needs
    to test logs.

    :type context: HackedContext
    log_name -- the name of the logs to clear (e.g. logcat)
    """

    log_system = context.driver.get_log(log_name)
