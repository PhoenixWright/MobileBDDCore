import time

from behave import *
from selenium.webdriver.support.ui import WebDriverWait


@step(u'I wait {wait_time} second')
@step(u'I wait {wait_time} seconds')
def _step(context, wait_time):
    """
    :type context: HackedContext
    :param wait_time: number of seconds to wait
    """
    wait_time = float(wait_time)
    time.sleep(wait_time)

@then(u'{element} should appear within {wait_time} seconds')
@then(u'{element} should appear in time')
@step(u'I wait for {element} to appear')
@step(u'I wait for {element} to be visible')
@step(u'I wait {wait_time} seconds for {element} to appear')
@step(u'I wait {wait_time} seconds for {element} to be visible')
def _step(context, wait_time=20, element=None):
    """
    :type context: HackedContext
    :param wait_time: number of seconds to wait. Defaults to 20
    :param element: identifier for the element we're waiting for
    """

    # This closure is so we can pass a callable object (that accepts the
    # driver) to until() below and still have access to the element we're
    # looking for.
    def isDisplayed(driver):
        return driver.simple_find(element).is_displayed()

    visible = WebDriverWait(context.driver, float(wait_time)).until(isDisplayed)
    assert visible, u'{} did not appear within {} seconds'.format(element, wait_time)
