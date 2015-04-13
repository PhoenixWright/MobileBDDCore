"""
overloaded hacks for webdriver stuff
"""
from __future__ import division

import logging
import os

from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
import time

from mobilebdd.behave_tools import slugify
from mobilebdd.steps.input import switch_to


log = logging.getLogger(u'mobilebdd')


class HackedWebDriver(WebDriver):
    """
    overloaded webdriver to add our own stuff
    """
    CommandExec = u'http://localhost:4444/wd/hub'
    ImplicitWait_sec = 10
    # fast implicit wait when using the simple search (which runs through
    # various find_element_by options)
    # 0 will turn implicit waits off, which is the default behavior. we want to
    # do this so we can quickly iterate through all the possible permuations of
    # ids. especially when there are multiple contexts in the app (eg. webviews)
    QuickImplicitWait_sec = 0
    # max time to allow when iterating through all the possible ways to find
    # something
    MaxSmartSearchTime_sec = 10
    # order of functions to call when searching for a 'thing'
    ElementSearchOrder = [
        u'find_element_by_id',
        u'find_element_by_xpath',
        u'find_element_by_link_text',
        u'find_element_by_partial_link_text',
        u'find_element_by_name',
        u'find_element_by_accessibility_id',
        u'find_element_by_tag_name',
        u'find_element_by_class_name',
        u'find_element_by_css_selector'
    ]
    # relative ending x,y coords for swiping gestures
    SwipeEndCoords = {
        u'left': (0.1, 0.5),
        u'right': (0.9, 0.5),
        u'up': (0.5, 0.1),
        u'down': (0.5, 0.9)
    }
    SwipeStartCoords = {
        u'left': (0.9, 0.5),
        u'right': (0.1, 0.5),
        u'up': (0.5, 0.9),
        u'down': (0.5, 0.1)
    }

    def __init__(self, **kwargs):
        """
        simplifies the setup for a webdriver a little bit

        :param device_type: phone vs. tablet
        :param os_ver: of device to connect to
        :param os_type: of device to connect to
        :param app_path: path to app to install onto the device
        :param app_package: for android, the package of the app to start
        :param app_activity: for android, the activity of the app to start
        :param webdriver_url: url to hit for webdriver nodes/grids
            if not given, will assume a selenium grid is running on localhost
        :param default_capabilities: whether or not to set up some boilerplate capabilities
            defaults to True
        """
        device_type = kwargs.get(u'device_type', None)
        os_ver = kwargs.get(u'os_ver', None)
        os_type = kwargs[u'os_type'].strip().lower()
        webdriver_url = kwargs.get(u'webdriver_url', None)
        webdriver_processor = kwargs.get(u'webdriver_processor', None)
        default_capabilities = kwargs.get(u'default_capabilities', True)

        caps = {}
        caps.update(self.setup_capabilities(**kwargs))

        # add os version
        assert os_ver
        os_ver = os_ver.strip().lower()

        if default_capabilities:
            # used for Appium 1.1+
            caps[u'deviceName'] = u' '.join([os_type, os_ver])

            # used to specify phone vs. tablet, only set if it's actually a string
            if device_type:
                caps[u'deviceType'] = device_type

            # used for Appium
            caps[u'platformVersion'] = os_ver

            # this is needed to work with selenium grid. appium 1.x ignores these
            # and uses platformVersion
            caps[u'version'] = os_ver

            # default to appium automation engine if not given
            if u'automationName' not in caps:
                caps[u'automationName'] = u'Appium'

        if not webdriver_url:
            webdriver_url = HackedWebDriver.CommandExec

        # if the user has specified a processor object, let the processor process
        # capabilities
        if webdriver_processor:
            log.debug(u'calling user-specified webdriver_processor.process_capabilities')
            caps = webdriver_processor.process_capabilities(caps)
            log.debug(u'updated capabilities: {}'.format(caps))

        # ok we now have the desired caps, lets actually create the webdriver
        log.debug(u'creating webdriver instance with capabilities: {}'.format(caps))
        super(HackedWebDriver, self).__init__(command_executor=webdriver_url, desired_capabilities=caps)
        # lengthen this wait to account for transient load issues on mobile
        self.implicitly_wait(HackedWebDriver.ImplicitWait_sec)

        # save these for later possible use
        self.os_ver = os_ver
        self.device = os_type
        self.num_screens = 0

    def setup_capabilities(self, **kwargs):
        """
        optional abstraction to setup capabilities dict
        """
        return {}

    def _simple_find_core(self, ref, context):
        """
        Iterates through all the possible find operations to locate an element
        within a context.  This method does not modify the wait time, nor does
        it keep trying for a while until timing out.  Both of these are nice
        features, so you should use simple_find or simple_find_in_context
        rather than using this method directly.

        :param ref: an identifier for an element; id, class name, partial link text, etc.
        :param context: the context in which we're looking; typically WEBVIEW or NATIVE_APP
        :rtype: WebElement
        """
        log.debug(u'switching to context ' + context)
        switch_to(self, context)

        for method in HackedWebDriver.ElementSearchOrder:
            try:
                element = getattr(self, method)(ref)
                if element:
                    return element
            except Exception:
                log.debug(u'couldnt {}. moving on...'.format(method))

    def simple_find(self, ref):
        """
        this simplifies the 'find' operation. from a behavioral/user pov, they
        should not know or care about how or where somethign is defined in the ui
        hierarchy/dom/whatever. they just want to perform an action on a Thing.
        this function makes it take simple by basically iterating through a bunch
        of possible ways to find the 'thing'

        this also considers any webviews in the app. starts with native, then
        goes through each 'context'

        @param ref: an identifier for an element; id, class name, partial link text, etc.
        @rtype: WebElement
        """
        contexts = list(self.contexts)

        # cut out all the extra webviews if there are any, and we're looking at a hybrid app
        if u'NATIVE_APP' in contexts and [webview for context in contexts if u'WEBVIEW' in contexts]:
            log.debug(u"replacing context list {} with simplified [u'NATIVE_APP', u'WEBVIEW'] list".format(contexts))
            contexts = [u'NATIVE_APP', u'WEBVIEW']

        # speed up the implicit wait, because with default time, this takes way
        # too long because of all the possible permutations
        self.implicitly_wait(HackedWebDriver.QuickImplicitWait_sec)

        # wrap this all in a try so we can restore the default implicit wait if
        # and when this block exits
        try:
            timeout = time.time() + self.MaxSmartSearchTime_sec
            while time.time() < timeout:
                for context in contexts:
                    element = self._simple_find_core(ref, context)
                    if element:
                        return element
                log.debug(u'exhausted all search permutations, looping until we timeout here')
        finally:
            # restore the default implicit wait
            self.implicitly_wait(HackedWebDriver.ImplicitWait_sec)

        raise NoSuchElementException(u'couldnt find {}!'.format(ref))

    def simple_find_in_context(self, ref, context):
        """
        Like simple_find, but limits the search to a specific context.  Useful
        for when you want to (e.g.) make sure you only look in the webview.

        :param ref: an identifier for an element; id, class name, partial link text, etc.
        :param context: the context in which we're looking; typically WEBVIEW or NATIVE_APP
        :rtype: WebElement
        """
        # speed up the implicit wait, because with default time, this takes way
        # too long because of all the possible permutations
        self.implicitly_wait(HackedWebDriver.QuickImplicitWait_sec)

        # wrap this all in a try so we can restore the default implicit wait if
        # and when this block exits
        try:
            timeout = time.time() + self.MaxSmartSearchTime_sec
            while time.time() < timeout:
                element = self._simple_find_core(ref, context)
                if element:
                    return element
                log.debug(u'exhausted all search methods, looping until we timeout here')
        finally:
            # restore the default implicit wait
            self.implicitly_wait(HackedWebDriver.ImplicitWait_sec)

        assert False, u'couldnt find {}!'.format(ref)

    def get_screenshot_path(self, path, suffix=''):
        """
        :param path: path to save image into
        :param suffix: if given, will append this to the filename
        """
        # clean the suffix (urls, for instance, don't make for good filenames)
        suffix = slugify(suffix)

        self.num_screens += 1
        file_name = u'screenshot-{:03d}{}{}.png'.format(
            self.num_screens,
            u'' if not suffix else u'-',
            u'' if not suffix else suffix
        )
        file_path = os.path.join(path, file_name)

        return file_path

    def take_screenshot(self, path, suffix=''):
        """
        takes a screenshot

        :param path: path to save image into
        :param suffix: if given, will append this to the filename of the saved
            screenshot
        :return: the filepath to the screenshot
        """
        file_path = self.get_screenshot_path(path, suffix)
        # ive seen this bork hard when the driver doesn't have control of the
        # active window, causing the entire test to break
        # this can happen when you're on the home screen or in an app that you
        # cant control
        try:
            self.get_screenshot_as_file(file_path)
            return file_path
        except WebDriverException as e:
            log.warning(u'problem taking screenshot! {}'.format(e))
            return None

    def swipe(self, direction, percentage=50):
        """
        abstraction for performing swipe gestures

        this overloads the appium method. uses strings to make it simpler.

        this should be overloaded for special cases, like ios7 or selendroid

        :param direction: to swipe
        """
        start_x = self.SwipeStartCoords[direction][0];
        start_y = self.SwipeStartCoords[direction][1];
        end_x = self.SwipeEndCoords[direction][0];
        end_y = self.SwipeEndCoords[direction][1];
        diff_x = (end_x - start_x) * (1 - int(percentage)/100);
        diff_y = (end_y - start_y) * (1 - int(percentage)/100);
        start_x += diff_x;
        start_y += diff_y;

        log.debug(u'start x: {} end x: {}', start_x, end_x)

        super(HackedWebDriver, self).swipe(
            start_x,
            start_y,
            end_x,
            end_y
        )

    def type(self, string, thing=None):
        """
        abstraction for performing typing actions

        :param string: to type
        :param thing: element to type into. optional
        """
        if thing:
            element = self.simple_find(thing)
            element.clear()
            element.send_keys(string)
        else:
            self.switch_to.active_element()\
                .clear()\
                .send_keys(string)

    def press_button(self, button):
        """
        abstraction to press os-level buttons

        needs to be implemented by all child classes

        :param button: to press
        """
        raise NotImplementedError()
