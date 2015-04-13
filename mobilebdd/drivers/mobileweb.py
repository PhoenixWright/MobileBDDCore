import logging
import time

from mobilebdd.hacks.webdriver import HackedWebDriver
from mobilebdd.steps.input import switch_to


log = logging.getLogger(u'mobilebdd')


class ChromeWebDriver(HackedWebDriver):
    """For chrome on android."""

    ElementSearchOrder = [
        u'find_element_by_id',
        u'find_element_by_css_selector',
        u'find_element_by_link_text',
        u'find_element_by_partial_link_text',
        u'find_element_by_name',
        u'find_element_by_tag_name',
        u'find_element_by_class_name'
    ]

    def setup_capabilities(self, **kwargs):
        caps = {}
        caps[u'platformName'] = kwargs[u'os_type']
        caps[u'platformVersion'] = kwargs[u'os_ver']
        caps[u'browserName'] = kwargs[u'app_path']
        return caps

    def simple_find(self, ref):
        """
        simple_find override that uses window_handles and switch_to.window
        rather than contexts, because that is all chromedriver seems to
        support

        @param ref: thing to find
        @rtype: WebElement
        """
        try:
            timeout = time.time() + self.MaxSmartSearchTime_sec
            while time.time() < timeout:
                for handle in self.window_handles:
                    log.debug(u'switching to window_handle {}'.format(handle))
                    self.switch_to.window(handle)
                    for method in self.ElementSearchOrder:
                        try:
                            log.debug(u'calling {}'.format(method))
                            element = getattr(self, method)(ref)
                            if element:
                                return element
                            else:
                                log.debug(u'couldnt {}. moving on...'.format(method))
                        except Exception:
                            log.debug(u'couldnt {}. moving on...'.format(method))
                log.debug(u'exhausted all search permutations, looping '
                              u'until we timeout here')
        except:
            pass  # let the below assert occur

        assert False, u'couldnt find {}!'.format(ref)


class WebViewAppDriver(HackedWebDriver):
    """For WebViewApp on iOS."""

    ElementSearchOrder = [
        u'find_element_by_id',
        u'find_element_by_css_selector',
        u'find_element_by_link_text',
        u'find_element_by_partial_link_text',
        u'find_element_by_name',
        u'find_element_by_tag_name',
        u'find_element_by_class_name'
    ]

    def __init__(self, **kwargs):
        super(WebViewAppDriver, self).__init__(**kwargs)

        log.debug(u'switching to webview context')
        self.switch_to.context(u'NATIVE_APP')
        switch_to(self, u'WEBVIEW')

    def setup_capabilities(self, **kwargs):
        caps = {}
        caps[u'platformName'] = kwargs[u'os_type']
        caps[u'platformVersion'] = kwargs[u'os_ver']
        caps[u'app'] = kwargs[u'app_path']
        return caps

    def simple_find(self, ref):
        """
        simple_find override that uses window_handles and switch_to.window
        rather than contexts, because that is all chromedriver seems to
        support

        :param ref: thing to find
        :rtype: WebElement
        """
        try:
            timeout = time.time() + self.MaxSmartSearchTime_sec
            while time.time() < timeout:
                for handle in self.window_handles:
                    log.debug(u'switching to window_handle {}'.format(handle))
                    self.switch_to.window(handle)
                    for method in self.ElementSearchOrder:
                        try:
                            log.debug(u'calling {}'.format(method))
                            element = getattr(self, method)(ref)
                            if element:
                                return element
                            else:
                                log.debug(u'couldnt {}. moving on...'.format(method))
                        except Exception:
                            log.debug(u'couldnt {}. moving on...'.format(method))
                log.debug(u'exhausted all search permutations, looping '
                              u'until we timeout here')
        except:
            pass  # let the below assert occur

        assert False, u'couldnt find {}!'.format(ref)

    def get_screenshot_as_file(self, filename):
        """
        When using WebViewApp, screenshots only work in the native context.
        """
        log.debug(u'switching to native context')
        self.switch_to.context(u'NATIVE_APP')

        log.debug(u'calling base get_screenshot_as_file')
        super(WebViewAppDriver, self).get_screenshot_as_file(filename)

        log.debug(u'switching back to webview context')
        switch_to(self, u'WEBVIEW')
