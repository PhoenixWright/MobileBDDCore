import logging
import time

from selenium import webdriver

from mobilebdd.hacks.webdriver import HackedWebDriver


log = logging.getLogger(u'mobilebdd')


DesktopElementSearchOrder = [
    u'find_element_by_id',
    u'find_element_by_css_selector',
    u'find_element_by_xpath',
    u'find_element_by_link_text',
    u'find_element_by_partial_link_text',
    u'find_element_by_name',
    u'find_element_by_tag_name',
    u'find_element_by_class_name'
]

def desktop_simple_find(driver, ref):
    """
    simple_find override that uses window_handles and switch_to.window
    rather than contexts, because that is all chromedriver seems to
    support

    :param driver: the webdriver to use for finding
    :param ref: thing to find
    :rtype: WebElement
    """
    try:
        timeout = time.time() + driver.MaxSmartSearchTime_sec
        while time.time() < timeout:
            for handle in driver.window_handles:
                log.debug(u'switching to window_handle {}'.format(handle))
                driver.switch_to.window(handle)
                for method in driver.ElementSearchOrder:
                    try:
                        log.debug(u'calling {}'.format(method))
                        element = getattr(driver, method)(ref)
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


class DesktopChromeWebDriver(HackedWebDriver):
    """For chrome on desktop."""

    ElementSearchOrder = DesktopElementSearchOrder

    def __init__(self, **kwargs):
        """
        simplifies the setup for a webdriver a little bit
        """
        super(DesktopChromeWebDriver, self).__init__(
            default_capabilities=False,  # ensure that HackedWebDriver doesn't mess with the capabilities
            **kwargs
        )

    def setup_capabilities(self, **kwargs):
        chrome_options = webdriver.ChromeOptions()

        user_agent = kwargs.get(u'user_agent', None)
        if user_agent:
            log.debug(u'adding user agent {} to chrome options'.format(user_agent))
            chrome_options.arguments.append(u'--user-agent={}'.format(user_agent))

        window_size_x = kwargs.get(u'window_size_x', None)
        window_size_y = kwargs.get(u'window_size_y', None)
        if window_size_x and window_size_y:
            log.debug(u'adding window size ({},{}) to chrome options'.format(window_size_x, window_size_y))
            chrome_options.arguments.append(u'--window-size={},{}'.format(window_size_x, window_size_y))

        return chrome_options.to_capabilities()

    def simple_find(self, ref):
        """
        simple_find override that uses window_handles and switch_to.window
        rather than contexts, because that is all chromedriver seems to
        support

        :param ref: thing to find
        :rtype: WebElement
        """
        return desktop_simple_find(self, ref)


class DesktopFirefoxWebDriver(HackedWebDriver):
    """For firefox on desktop."""

    ElementSearchOrder = DesktopElementSearchOrder

    def __init__(self, **kwargs):
        """
        simplifies the setup for a webdriver a little bit
        """
        super(DesktopFirefoxWebDriver, self).__init__(
            default_capabilities=False,  # ensure that HackedWebDriver doesn't mess with the capabilities
            **kwargs
        )

    def setup_capabilities(self, **kwargs):
        caps = webdriver.DesiredCapabilities().FIREFOX
        return caps

    def simple_find(self, ref):
        """
        simple_find override that uses window_handles and switch_to.window
        rather than contexts, because that is all chromedriver seems to
        support

        :param ref: thing to find
        :rtype: WebElement
        """
        return desktop_simple_find(self, ref)


class DesktopInternetExplorerWebDriver(HackedWebDriver):
    """For internet explorer on desktop."""

    ElementSearchOrder = DesktopElementSearchOrder

    def __init__(self, **kwargs):
        """
        simplifies the setup for a webdriver a little bit
        """
        super(DesktopInternetExplorerWebDriver, self).__init__(
            default_capabilities=False,  # ensure that HackedWebDriver doesn't mess with the capabilities
            **kwargs
        )

    def setup_capabilities(self, **kwargs):
        caps = webdriver.DesiredCapabilities().INTERNETEXPLORER

        # this is what would be necessary to run via STS
        #caps['browserName'] = '*iexplore'

        return caps

    def simple_find(self, ref):
        """
        simple_find override that uses window_handles and switch_to.window
        rather than contexts, because that is all chromedriver seems to
        support

        :param ref: thing to find
        :rtype: WebElement
        """
        return desktop_simple_find(self, ref)
