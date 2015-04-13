"""
steps for doing gestures on diff devices
"""

from behave import *
import logging
from selenium import webdriver
from selenium.webdriver.common.touch_actions import TouchActions
from mobilebdd.drivers.ios import iOSWebDriver


log = logging.getLogger(u'mobilebdd')

directions = {u'left' : [(300, 300), (  0, 300)],
              u'right': [(  0, 300), (300, 300)],
              u'up'   : [(300, 300), (300,   0)],
              u'down' : [(300, 300), (300, 600)]}

@step(u'I swipe {direction}')
@step(u'I swipe to the {direction}')
@step(u'I swipe {direction} through {percentage} percent of screen')
def _scroll(context, direction, percentage=50):
    """
    :type context: HackedContext
    """
    if isinstance(context.driver, iOSWebDriver):
        context.driver.swipe(direction, percentage)
    else:
        touch_action = TouchActions(context.driver).tap_and_hold(directions[direction][0][0], directions[direction][0][1])
        touch_action.move(directions[direction][1][0], directions[direction][1][1])
        touch_action.release(directions[direction][1][0], directions[direction][1][1])
        touch_action.perform()


@step(u'I scroll up')
def _step(context):
    """
    :type context: HackedContext
    """
    # this is the effect of swiping down
    context.execute_steps(u'''
        When I swipe down
    ''')


@step(u'I scroll down')
def _step(context):
    """
    :type context: HackedContext
    """
    # this is the effect of swiping up
    context.execute_steps(u'''
        When I swipe up
    ''')
