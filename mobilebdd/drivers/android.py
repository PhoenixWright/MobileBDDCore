"""
android webdrivers
"""
import logging

from selenium.webdriver import TouchActions
from mobilebdd.hacks.webdriver import HackedWebDriver


log = logging.getLogger(u'mobilebdd')


class AndroidWebDriver(HackedWebDriver):
    """
    webdriver for non-selendroid appium nodes
    """

    # mapping of names to android keycodes
    # http://developer.android.com/reference/android/view/KeyEvent.html
    AndroidButtons = {
        u'home': 3,
        u'back': 4,
        u'menu': 82,
        u'enter': 66
    }

    def setup_capabilities(self, **kwargs):
        caps = {
            # for appium 1.x
            u'platformName': u'Android',
            # for selenium grid
            u'platform': u'ANDROID'
        }

        if u'app_path' in kwargs:
            caps[u'app'] = kwargs[u'app_path']
        if u'app_package' in kwargs:
            caps[u'appPackage'] = kwargs[u'app_package']
        if u'app_activity' in kwargs:
            caps[u'appActivity'] = kwargs[u'app_activity']

        return caps

    def press_button(self, button):
        button = button.lower()

        assert button in self.AndroidButtons,\
            u'{} is unknown! Contact us to implement if critical.'.format(button)

        self.keyevent(self.AndroidButtons[button])


class SelendroidWebDriver(AndroidWebDriver):
    """
    webdriver for selendroid (android < 4.2 on appium)

    http://selendroid.io/gestures.html
    """

    # predef x,y flick speeds
    FlickSpeeds = {
        u'left': (100, 0),
        u'right': (-100, 0),
        u'up': (0, -100),
        u'down': (0, 100)
    }

    def setup_capabilities(self, **kwargs):
        caps = super(SelendroidWebDriver, self).setup_capabilities(**kwargs)
        caps[u'automationName'] = u'Selendroid'
        return caps

    # override this because selendroid has its own way of doing swipes/flicks
    def swipe(self, direction):
        touch = TouchActions(self)
        touch.flick(
            self.FlickSpeeds[direction][0],
            self.FlickSpeeds[direction][1]
        )
        touch.perform()
