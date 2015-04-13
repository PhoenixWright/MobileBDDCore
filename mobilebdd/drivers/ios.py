"""
ios webdrivers
"""
from mobilebdd.hacks.webdriver import HackedWebDriver


class iOSWebDriver(HackedWebDriver):
    """
    webdriver for ios
    """

    def setup_capabilities(self, **kwargs):
        caps = {u'platformName': u'iOS'}

        if u'app_path' in kwargs:
            caps[u'app'] = kwargs[u'app_path']

        return caps

    def swipe(self, direction, percentage=50):
        # appium 1.x removed 'mobile:' script events. so they should've fixed
        # this. test it sometime, will ya?
        # # ios 7 broke existing swipe functionality. have to use scroll
        # # the future is here
        # if self.os_ver == '7.0':
        #     self.execute_script('mobile: scroll', {
        #         'direction': direction
        #     })
        # else:
        super(iOSWebDriver, self).swipe(direction, percentage)

    def press_button(self, button):
        assert False,\
            u'hardware button presses are not supported on ios'
            # it's stupid but/and it's true
