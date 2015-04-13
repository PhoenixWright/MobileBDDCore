"""
steps for pressing a device's buttons and sending input
"""

from behave import *
from selenium.webdriver.support.ui import Select
import logging
import json
import time


log = logging.getLogger(u'mobilebdd')


@step(u'I browse to {url}')
@step(u'I go to {url}')
def _step(context, url):
    """
    :type context: HackedContext
    """
    context.driver.get(url)


@step(u'I press {button}')
@step(u'I press the {button} button')
def _step(context, button):
    """
    :type context: HackedContext
    """
    context.driver.press_button(button)


@step(u'I type {string} in {thing}')
@step(u'I type {string} into {thing}')
def _step(context, string, thing):
    """
    :type context: HackedContext
    """
    context.driver.type(string, thing)


@step(u'I tap on {thing}')
def _step(context, thing):
    """
    :type context: HackedContext
    """
    # find the element
    element = context.driver.simple_find(thing)
    assert element, u'No element found that matched "{}"'.format(thing)

    # This if condition is specifically to hack around the fact that clicks
    # in iOS webviews may or may not work depending on the version of Appium
    # being used. The safest route is to use the coordinates of the iOS web
    # element plus the offset of the iOS webview to tap the right spot of the
    # screen in the native context.
    log.debug(u'checking if the os_type is ios and we are in a webview')
    if context.os_type.lower() == u'ios' and context.driver.current_context is not None and u'WEBVIEW' in context.driver.current_context:
        log.debug(u'running ios workaround to tap webview elements in the native context because webview clicks sometimes do not work')

        # extract the element position information
        element_pos = element.location
        element_size = element.size
        log.debug(u'element position: ({}, {}) and size: {}x{}'.format(element_pos[u'x'], element_pos[u'y'], element_size[u'width'], element_size[u'height']))

        # switch to the native context
        switch_to(context.driver, u'NATIVE_APP')

        # find the scrollview containing the UIAWebView in the native context
        # so that we can offset the tap on the webview element with its x and y coordinates
        # the webview coordinates x and y actually represent how much the webview has scrolled, or we'd use those
        webview = context.driver.find_element_by_class_name(u'UIAScrollView')
        webview_pos = webview.location
        webview_size = webview.size
        log.debug(u'webview position: ({}, {}) and size {}x{}'.format(webview_pos[u'x'], webview_pos[u'y'], webview_size[u'width'], webview_size[u'height']))

        # tap the middle of the element
        tap_x = element_pos[u'x'] + element_size[u'width'] / 2 + webview_pos[u'x']
        tap_y = element_pos[u'y'] + element_size[u'height'] / 2 + webview_pos[u'y']
        log.debug(u'tapping the native context at ({}, {})'.format(tap_x, tap_y))
        context.driver.tap([(tap_x, tap_y)])

        # switch back to the webview
        switch_to(context.driver, u'WEBVIEW')
    else:
        # normal implementation
        log.debug(u'calling {}.click()'.format(element))
        element.click()

@step(u'I tap coordinate {x},{y}')
def _step(context, x, y):
    """
    :type context: HackedContext
    """
    # tap on the coordinate
    context.driver.tap([(x, y)])

@step(u'I scroll to {thing}')
def _step(context, thing):
    """
    :type context: HackedContext
    """
    # scrolling to an element will land the user with the element at the top of
    # the page. so scrolling to the element itself won't leave any context about
    # what is above the element. this variable is how much 'space' above the element
    # should be left
    SCROLL_OFFSET = 100

    element = context.driver.simple_find(thing)
    assert element, u'No element found that matched "{}"'.format(thing)
    context.driver.execute_script(u'window.scrollTo(0, {});'.format(element.location[u'y'] - SCROLL_OFFSET))

    # scrolling has a pretty serious delay, and we don't want to capture a screenshot until after it is over
    time.sleep(5)


@step(u'I select {value} from drop-down {dropdown}')
@step(u'I select {value} from dropdown {dropdown}')
def _step(context, value, dropdown):
    """
    :type context: HackedContext
    """
    element = context.driver.simple_find(dropdown)
    assert element, u'No dropdown found that matched "{}"'.format(dropdown)
    select_element = Select(element)
    select_element.select_by_value(value)


def switch_to(driver, context_name):
    """
    :type context: HackedContext
    """

    log.debug(u'getting the list of contexts to attempt to match against "{}"'.format(context_name))
    app_contexts = driver.contexts
    log.debug(u'attempting to switch to "{}", available contexts: {}'.format(context_name, app_contexts))

    # reverse the contexts so they represent the most recent ones first
    for app_context in reversed(app_contexts):
        if context_name.lower() in app_context.lower():
            log.debug(u'switching to context "{}"'.format(app_context))
            driver.switch_to.context(app_context)
            return

    assert False, u'failed to switch to context "{}". available contexts: {}'.format(context_name, app_contexts)


@step(u'I switch to the {context_name} context')
def _step(context, context_name):
    """
    :type context: HackedContext
    """

    switch_to(context.driver, context_name)


@step(u'I add the cookie {cookie}')
def _step(context, cookie):
    """
    :type context: HackedContext
    """

    log.debug(u'loading "{}" into json to use with webdriver.add_cookie'.format(cookie))
    cookie = json.loads(cookie)

    log.debug(u'loaded json "{}", adding cookie'.format(cookie))
    context.driver.add_cookie(cookie)


@step(u'I delete all cookies')
def _step(context):
    """
    :type context: HackedContext
    """
    log.debug(u'deleting all cookies')
    context.driver.delete_all_cookies()



@step(u'I add the weblab {cookie}')
@step(u'I add the weblab {cookie} on the domain {url}')
def _step(context, cookie, url=None):
    """
    :type context: HackedContext
    """
    if url:
        context.driver.get(url)

    log.debug(u'deleting all cookies')
    context.driver.delete_all_cookies()

    log.debug(u'loading "{}" into json to use with webdriver.add_cookie'.format(cookie))
    cookie = json.loads(cookie)

    log.debug(u'loaded json "{}", adding cookie'.format(cookie))
    context.driver.add_cookie(cookie)

    log.debug(u'refreshing current page')
    context.driver.get(context.driver.current_url)


@then(u'the cookie {cookie_name} should have the value {cookie_value}')
def _step(context, cookie_name, cookie_value):
    """
    :type context: HackedContext
    """
    log.debug(u'getting cookie with name "{}"'.format(cookie_name))
    cookie = context.driver.get_cookie(cookie_name)

    log.debug(u'cookie: {}'.format(cookie))
    assert cookie[u'value'] == cookie_value


@step(u'I execute the Javascript {script} with no arguments')
@step(u'I execute the JS {script} with no arguments')
def _step(context, script):
    """
    :type context: HackedContext
    :param script: arbitrary JavaScript to execute within the webview
    """
    log.debug(u'executing script "{}" in webview'.format(script))
    context.driver.execute_script(script)


# Script arguments passed to this call will be exposed in the script using the arguments[] array.
# So your script text might look like this:
#   someFunction(arguments[0], arguments[1])
@step(u'I execute the Javascript {script} with arguments {args}')
@step(u'I execute the JS {script} with arguments {args}')
def _step(context, script, args):
    """
    :type context: HackedContext
    :param script: arbitrary JavaScript to execute within the webview.
    :param args: comma-separated arguments to be passed to the script call, e.g. "foo, bar"
    """
    log.debug(u'executing script "{}" in webview'.format(script))
    varargs = args.split(", ")
    context.driver.execute_script(script, *varargs)

@step(u'I check the {checkbox} checkbox')
def _step(context, checkbox):
    """
    Checks the defined checkbox, if the checkbox is found and not already checked.
    A NoSuchElementException will be thrown if the checkbox is not found.
    :type context: HackedContext
    :param checkbox: The checkbox to check
    """
    # find the element
    element = context.driver.simple_find(checkbox)

    checked = element.get_attribute('checked')
    if checked == u'false':
        element.click()

@step(u'I uncheck the {checkbox} checkbox')
def _step(context, checkbox):
    """
    Unchecks the defined checkbox, if the checkbox is found and not already unchecked.
    A NoSuchElementException will be thrown if the checkbox is not found.
    :type context: HackedContext
    :param checkbox: The checkbox to uncheck
    """
    # find the element
    element = context.driver.simple_find(checkbox)

    checked = element.get_attribute('checked')
    if checked == u'true':
        element.click()
