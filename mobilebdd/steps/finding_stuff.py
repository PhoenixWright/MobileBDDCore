"""
then/verification steps
"""

from behave import *
import logging
import ast
import re
import time
from selenium.common.exceptions import NoSuchElementException
from mobilebdd.steps.input import switch_to
from selenium.webdriver.support.ui import WebDriverWait


log = logging.getLogger(u'mobilebdd')


# mapping of relative regions that define the start and end to determine
# if an element is in a region
SearchRegions = {
    u'top': (u'y', 0, 0.5),
    u'bottom': (u'y', 0.5, 1),
    u'right': (u'x', 0.5, 1),
    u'left': (u'x', 0, 0.5),
}


@then(u'{element} should appear')
@then(u'{element} should be visible')
@then(u'{element} should not be hidden')
def _step(context, element):
    """
    :type context: HackedContext
    """
    assert context.driver.simple_find(element).is_displayed(),\
        '{} should be present and displayed'.format(element)


@then(u'{element} should be hidden')
@then(u'{element} should not appear')
@then(u'{element} should not be visible')
def _step(context, element):
    """
    :type context: HackedContext
    """
    try:
        item = context.driver.simple_find(element)
        assert not item.is_displayed(),\
            u'{} should not be present and displayed'.format(element)
    except NoSuchElementException:
        pass


@then(u'{element} should be selected')
def _step(context, element):
    """
    :type context: HackedContext
    """
    assert context.driver.simple_find(element).is_selected(),\
        u'{} should be selected'.format(element)


@then(u'{element} should not be selected')
def _step(context, element):
    """
    :type context: HackedContext
    """
    assert not context.driver.simple_find(element).is_selected(),\
        u'{} should not be selected'.format(element)


def _is_element_in_webview_region(context, thing, location):
    """
    checks if the element is in the region of the webview described by 'location'

    :type context: HackedContext
    :param thing: an identifier for an element; id, class name, partial link text, etc.
    :param location: one of top, bottom, left, right, center, viewport
    :return True/False
    """
    try:
        element = context.driver.simple_find_in_context(thing, u'WEBVIEW')
    except Exception:
        return False
    # To correctly find an element within a webview region, we need the size of
    # the webview as reported by script within the webview itself.  This
    # provides a value of the same pixel density used when finding the element,
    # so that the arithmetic is correct when we compare those values later.
    window_size = {
        u'width':  float(context.driver.execute_script(u'return document.documentElement.clientWidth')),
        u'height': float(context.driver.execute_script(u'return document.documentElement.clientHeight'))
    }
    return _is_element_in_region(element, window_size, location)


def _is_element_in_native_region(context, thing, location):
    """
    checks if the element is in the region of the app described by 'location'

    :type context: HackedContext
    :param thing: an identifier for an element; id, class name, partial link text, etc.
    :param location: one of top, bottom, left, right, center, viewport
    :return True/False
    """
    try:
        element = context.driver.simple_find_in_context(thing, u'NATIVE_APP')
    except Exception:
        return False
    window_size = context.driver.get_window_size()
    return _is_element_in_region(element, window_size, location)


def _is_element_in_region(element, window_size, location):
    """
    checks if the element is in the region of the window described by 'location'

    :param element: the app or webview element in question
    :param window_size: an object with width and height properties
    :param location: one of top, bottom, left, right, center, viewport
    :return True/False
    """
    # For starters, check if the element is even displayed.
    if not element.is_displayed():
        return False

    element_pos = element.location
    element_size = element.size
    window_width = float(window_size[u'width'])
    window_height = float(window_size[u'height'])
    element_top = element_pos[u'y'] / window_height
    element_bottom = element_top + element_size[u'height'] / window_height
    element_left = element_pos[u'x']/ window_width
    element_right = element_left + element_size[u'width'] / window_width

    log.info(u'element position: x {}, y {}'.format(element_pos[u'x'], element_pos[u'y']))
    log.info(u'element dimensions: width {}, height {}'.format(element_size[u'width'], element_size[u'height']))
    log.info(u'window dimensions: width {}, height {}'.format(window_size[u'width'], window_size[u'height']))
    log.info(u'expecting to find the element at {}'.format(location))
    log.info(u'element bounds: top {}, left {}, right {}, bottom {}'.format(
        element_top, element_left, element_right, element_bottom
    ))

    is_correct = True

    if location == u'center':
        return element_top > 0.3\
            and element_bottom < 0.7\
            and element_left > 0.3\
            and element_right < 0.7
    elif location == u'viewport':
        return element_top >= 0\
            and element_bottom <= 1\
            and element_left >= 0\
            and element_right <= 1
    else:
        for location_word in location.split():
            if location_word not in SearchRegions:
                log.error(u'unsupported location {}'.format(location))
                return False

            region = SearchRegions[location_word]
            if region[0] == u'y':
                return element_top >= region[1] and element_bottom <= region[2]
            else:
                return element_left >= region[1] and element_right <= region[2]

    return is_correct


@then(u'{thing} should be at the {location} of the webview')
@then(u'{thing} should be in the {location} of the webview')
def _step(context, thing, location):
    """
    :type context: HackedContext
    :param thing: an identifier for an element; id, class name, partial link text, etc.
    :param location: one of top, bottom, left, right, center, viewport
    """
    is_correct = _is_element_in_webview_region(context, thing, location)
    assert is_correct, u'{} was not at {}'.format(thing, location)


@then(u'{thing} should be at the {location} of the app')
@then(u'{thing} should be in the {location} of the app')
def _step(context, thing, location):
    """
    :type context: HackedContext
    :param thing: an identifier for an element; id, class name, partial link text, etc.
    :param location: one of top, bottom, left, right, center, viewport
    """
    is_correct = _is_element_in_native_region(context, thing, location)
    assert is_correct, u'{} was not at {}'.format(thing, location)


@then(u'{thing} should not be at the {location} of the webview')
@then(u'{thing} should not be in the {location} of the webview')
def _step(context, thing, location):
    """
    :type context: HackedContext
    :param thing: an identifier for an element; id, class name, partial link text, etc.
    :param location: one of top, bottom, left, right, center, viewport
    """
    is_correct = _is_element_in_webview_region(context, thing, location)
    assert not is_correct, u'{} was at {}'.format(thing, location)


@then(u'{thing} should not be at the {location} of the app')
@then(u'{thing} should not be in the {location} of the app')
def _step(context, thing, location):
    """
    :type context: HackedContext
    :param thing: an identifier for an element; id, class name, partial link text, etc.
    :param location: one of top, bottom, left, right, center, viewport
    """
    is_correct = _is_element_in_native_region(context, thing, location)
    assert not is_correct, u'{} was at {}'.format(thing, location)


@then(u'{thing} should be inside {element} located at {location}')
def _step(context, thing, element, location):
    """
    :type context: HackedContext
    """

    item = context.driver.simple_find(thing)
    elem = context.driver.simple_find(element)

    itemCorner = item.location
    elemCorner = elem.location

    if location == u'top-right':
        elemWidth = elem.size['width']
        itemWidth = item.size['width']
        elemCorner['x'] = elemCorner['x'] + elemWidth
        itemCorner['x'] = itemCorner['x'] + itemWidth
    elif location == u'top-center':
        elemWidth = elem.size['width']
        itemWidth = item.size['width']
        elemCorner['x'] = elemCorner['x'] + elemWidth / 2
        itemCorner['x'] = itemCorner['x'] + itemWidth / 2
    elif location == u'bottom-left':
        elemHeight = elem.size['height']
        itemHeight = item.size['height']
        elemCorner['y'] = elemCorner['y'] + elemHeight
        itemCorner['y'] = itemCorner['y'] + itemHeight
    elif location == u'bottom-right':
        elemWidth = elem.size['width']
        itemWidth = item.size['width']
        elemHeight = elem.size['height']
        itemHeight = item.size['height']
        elemCorner['x'] = elemCorner['x'] + elemWidth
        itemCorner['x'] = itemCorner['x'] + itemWidth
        elemCorner['y'] = elemCorner['y'] + elemHeight
        itemCorner['y'] = itemCorner['y'] + itemHeight
    elif location == u'bottom-center':
        elemWidth = elem.size['width']
        itemWidth = item.size['width']
        elemHeight = elem.size['height']
        itemHeight = item.size['height']
        elemCorner['x'] = elemCorner['x'] + elemWidth / 2
        itemCorner['x'] = itemCorner['x'] + itemWidth / 2
        elemCorner['y'] = elemCorner['y'] + elemHeight
        itemCorner['y'] = itemCorner['y'] + itemHeight
    elif location == u'center':
        elemWidth = elem.size['width']
        itemWidth = item.size['width']
        elemHeight = elem.size['height']
        itemHeight = item.size['height']
        elemCorner['x'] = elemCorner['x'] + elemWidth / 2
        itemCorner['x'] = itemCorner['x'] + itemWidth / 2
        elemCorner['y'] = elemCorner['y'] + elemHeight / 2
        itemCorner['y'] = itemCorner['y'] + itemHeight / 2
    elif location != u'top-left':
        assert False,u'{} is not a supported location'.format(location)

    xDiff = itemCorner['x'] - elemCorner['x']
    yDiff = itemCorner['y'] - elemCorner['y']

    # There may be rounding error, if any of the dimensions were odd numbers, so verify that they match within 1 pixel
    assert xDiff <= 1 and yDiff <= 1,\
        u'{} is not in expected location inside {} at {}. Expected at [{}, {}] but was at [{}, {}]'.format(thing, element, location, elemCorner['x'], elemCorner['y'], itemCorner['x'], itemCorner['x'])


@then(u'{thing} should contain the text {text}')
def _step(context, text, thing):
    """Assert that the given text is in the element found by searching for 'thing'.
    :type context: HackedContext
    """
    element = context.driver.simple_find(thing)
    assert element, u'could not find {}'.format(thing)
    assert text in element.text, u'specified text "{}" was not present in element text: "{}"'.format(text, element.text)

@then(u'{thing} should not contain the text {text}')
def _step(context, text, thing):
    """Assert that the given text is not in the element found by searching for 'thing'.
    :type context: HackedContext
    """
    element = context.driver.simple_find(thing)
    assert element, u'could not find {}'.format(thing)
    assert text not in element.text, u'specified text "{}" was present in element text: "{}"'.format(text, element.text)


@then(u'{thing} should contain the exact text {text}')
def _step(context, text, thing):
    """Assert that the given text is equal to the text in the element found by
    searching for 'thing'.
    :type context: HackedContext
    """
    element = context.driver.simple_find(thing)
    assert element, u'could not find {}'.format(thing)
    assert text == element.text, u'specified text "{}"" != element text "{}"'.format(text, element.text)


@then(u'{text} should be in the current url')
def _step(context, text):
    """
    :type context: HackedContext
    """
    assert text in context.driver.current_url,\
        u'"{}"" was not in the current url: {}'.format(text, context.driver.current_url)


@then(u'{text} should be in the page source')
def _step(context, text):
    """
    :type context: HackedContext
    """
    assert text in context.driver.page_source,\
        u'"{}" was not in the page source'.format(text)


@then(u'{thing} should have a {attribute} containing {text}')
@then(u'{thing} should have an {attribute} containing {text}')
def _step(context, thing, attribute, text):
    """
    :type context: HackedContext
    """
    element = context.driver.simple_find(thing)
    assert element, u'could not find {}'.format(thing)
    value = element.get_attribute(attribute)
    assert value, u'element did not have an attribute named {} or it was empty'.format(attribute)
    assert text in value, u'could not find the text "{}" in the "{}" attribute, real value: "{}"'.format(text, attribute, value)


def assert_text_appears_in_logs(context, text_array, log_name):
    """
    Tests that a list of strings each appear in the logs a specified number of times.
    Set the number of times to 0 to verify that text does not appear in the logs.
    
    :type context: HackedContext
    text_array -- A dictionary containing key/value pairs for a word and its expected frequency
    log_name -- the name of the log to search for the text in (e.g. logcat)
    """
    results = {}
    
    log_system = context.driver.get_log(log_name)
    for log_entry in log_system:
        for text_entry in text_array:
            if text_entry not in results:
                results[text_entry] = 0
            if text_entry in log_entry[u'message']:
                results[text_entry] += 1
                # If we've already exceeded the number of expected occurrences, we can fail right away.
                times = int(text_array[text_entry])
                if times < results[text_entry]:
                    assert False,\
                        u"Expected {} {} times in the {} logs, but the number of occurrences exceeded the expectation".format(text_entry, times, log_name)
            
    for text_entry in text_array:
        times = int(text_array[text_entry])
        if times >= 0:
            assert times == results[text_entry],\
                u"Expected {} {} times in the {} logs, but found it {} times".format(text_entry, times, log_name, results[text_entry])
        else:
            assert results[text_entry] > 0,\
                u"{} was not found in the {} logs".format(text_entry, log_name)
    

@then(u'the {log_name} logs will contain the following strings')
@then(u'the {log_name} logs will contain strings based on their frequencies listed in the following table')
def _step(context, log_name):
    """
    Tests that a list of strings each appear in the logs a specified number of times.
    Set the number of times to 0 to verify that text does not appear in the logs.

    Currently, we must call "I clear the {log_name} logs" at the beginning of your scenario
    or else this step may pick up spillover from previous scenarios
    TODO: In the future, we should make this extra log clearance call unnecessary by having the
    functionality included in a listener or by adding a simple way to automatically enable or
    disable log clearance ahead of time.
    
    This step expects that the user will pass in a table listing strings and frequencies.
    The table should be included immediately after the step is written out. Below is an example
    of what the step and table declaration might look like in practice:
    ...
    Then the logcat logs will contain the following strings
     | string    | frequency    |
     | Hello     | 1            |
     | Goodbye   | 0            |

    :type context: HackedContext
    log_name -- the name of the log to search for the text in (e.g. logcat)
    """
    text_array = {}
    for row in context.table:
        text_array[row['string']] = row['frequency']
    
    assert_text_appears_in_logs(context, text_array, log_name)


@then(u'the strings {text_json} should be in the {log_name} logs')
def _step(context, text_json, log_name):
    """
    Tests that a list of strings each appear in the logs a specified number of times.
    Set the number of times to 0 to verify that text does not appear in the logs.
    
    Currently, we must call "I clear the {log_name} logs" at the beginning of your scenario
    or else this step may pick up spillover from previous scenarios

    :type context: HackedContext
    text_json -- A JSON-formatted dictionary
        key -- text to search the logs for
        value -- number of times the text is expected to appear in the logs
        Example:
        {"'This' is the Expected Text":1,"More Text":0}
    log_name -- the name of the log to search for the text in (e.g. logcat)
    """
    assert_text_appears_in_logs(context, ast.literal_eval(text_json), log_name)


@then(u'{text} should be in the {log_name} logs')
@then(u'{text} should be in the {log_name} logs {times} time')
@then(u'{text} should be in the {log_name} logs {times} times')
@then(u'the following string should be in the {log_name} logs: {text}')
@then(u'the following string should be in the {log_name} logs {times} time: {text}')
@then(u'the following string should be in the {log_name} logs {times} times: {text}')
def _step(context, text, log_name, times = -1):
    """
    Tests that a string appears in the logs a specified number of times.
    Set the number of times to 0 to verify that text does not appear in the logs.

    For best results, call "I clear the {log_name} logs" at the beginning of your scenario, otherwise
    this step may pick up spillover from previous scenarios
    
    :type context: HackedContext
    text -- the exact text to search for in the logs
    log_name -- the name of the log to search for the text in (e.g. logcat)
    times -- the number of times the text is expected to appear in the logs. If not set, or set to < 0, the text will be expected at least once.
    """

    times = int(times)
    log_system = context.driver.get_log(log_name)
    found_times = 0
    for log_entry in log_system:
        if text in log_entry[u'message']:
            log.debug(u"String found in {}".format(log_entry[u'message']))
            found_times += 1
    
    if times >= 0:
        assert found_times == times,\
            u"Expected {} {} times in the {} logs, but found it {} times".format(text, times, log_name, found_times)
    else:
        assert found_times > 0,\
            u"{} was not found in the {} logs".format(text, log_name)


@then(u'{text} should not be in the {log_name} logs')
def _step(context, text, log_name):
    """
    Tests that a string does not appear in the logs.
    """
    context.run_steps('Then {} should be in the {} logs 0 times'.format(text, log_name))


@step('I save the {log_name} log message containing the text {regex} as {key}')
@step('I save the {log_name} log message matching the regular expression {regex} as {key}')
def _step(context, log_name, regex, key):
    '''
    Retrieves a log message containing the specified text and saves it to
    HackedContext's saved_data for later access. This enables steps executed
    after this step to access the found log message for further processing.

    :type context: HackedContext
    :param log_name: the name of the log to search for the text in (e.g. logcat)
    :param regex: the regular expression to match the log message to 
        - this can also be a string without regular expression notation as it will also match
    :param key: the key to save the message to in the context's saved_data
    '''
    log_system = context.driver.get_log(log_name)
    for log_entry in log_system:
        if re.search(regex, log_entry[u'message']):
            context.saved_data[key] = log_entry[u'message']
    assert context.saved_data[key], u"{} was not found in the {} logs".format(text, log_name)

@step('I verify {value} is in the context\'s list at {key}')
def _step(context, value, key):
    '''
    Verifies that the given value is not in the list stored at the 
    key of the context's saved_data
    :type context: HackedContext
    '''
    assert value in context.saved_data[key]

@step('I verify {value} is not in the context\'s list at {key}')
def _step(context, value, key):
    '''
    Verifies that the given value is not in the list stored at the 
    key of the context's saved_data
    :type context: HackedContext
    '''
    assert value not in context.saved_data[key]
        
@then(u'the {log_name} logs will contain the following strings in the same entry')
@then(u'the {log_name} logs will contain the following strings in the same line')
@then(u'the {log_name} logs will contain the following strings on the same line')
def _step(context, log_name):
    """
    Tests that each given substring appears in the logs in the same log entry.
    Each substring must appear at least once or else the assertion will fail.

    This step expects that the user will pass in a table of substrings.
    The table should be included immediately after the step is written out. Below is an example
    of what the step and table declaration might look like in practice:
    ...
    Then the logcat logs will contain the following strings in the same entry
     | string    |
     | Hello     |
     | Goodbye   |
     
    :type context: HackedContext
    log_name -- the name of the log to search for the text in (e.g. logcat)
    """
    text_list = []
    for row in context.table:
        text_list.append(row['string'])
    results = {}

    log_system = context.driver.get_log(log_name)
    all_strings_in_same_entry = False
    for log_entry in log_system:
        strings_present_so_far = True
        for text_entry in text_list:
            if re.search(text_entry, log_entry[u'message']) == None:
                strings_present_so_far = False
                break
        if strings_present_so_far == True:
            all_strings_in_same_entry = True
            break
            
    assert all_strings_in_same_entry, u"The strings were not present in the same entry of the {} logs".format(log_name)


def does_text_appear_in_logs(driver, text, log_name):
    log_system = driver.get_log(log_name)
    for log_entry in log_system:
        if text in log_entry[u'message']:
            return True
    return False


@step(u'I wait until {text} appears in the {log_name} logs')
@step(u'I wait until the following text appears in the {log_name} logs: {text}')
@step(u'{text} will eventually appear in the {log_name} logs')
@step(u'I wait until {text} appears in the {log_name} logs within {wait_time} seconds')
@step(u'I wait until the following text appears in the {log_name} logs within {wait_time} seconds: {text}')
@step(u'{text} will eventually appear in the {log_name} logs within {wait_time} seconds')
def _step(context, text, log_name, wait_time=20):
    """
    Waits for a string to appear in the logs within some time limit. Time limit defaults to 20 seconds.
    """
    def isDisplayed(driver):
        return does_text_appear_in_logs(driver, text, log_name)

    visible = WebDriverWait(context.driver, float(wait_time)).until(isDisplayed)
    assert visible, u'{} did not appear in the {} logs within {} seconds'.format(element, log_name, wait_time)
