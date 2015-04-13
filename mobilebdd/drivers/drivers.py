import logging

from mobilebdd.drivers.android import AndroidWebDriver, SelendroidWebDriver
from mobilebdd.drivers.desktop import DesktopChromeWebDriver, DesktopInternetExplorerWebDriver, DesktopFirefoxWebDriver
from mobilebdd.drivers.ios import iOSWebDriver
from mobilebdd.drivers.mobileweb import ChromeWebDriver, WebViewAppDriver
from mobilebdd.hacks.webdriver import HackedWebDriver


log = logging.getLogger(u'mobilebdd')


# mapping of device types to custom, specific webdrivers
HackedDrivers = {
    u'android': AndroidWebDriver,
    u'selendroid': SelendroidWebDriver,
    u'ios': iOSWebDriver,
    u'ipad': iOSWebDriver,
    u'iphone': iOSWebDriver,

    # mobile browsers
    u'chrome': ChromeWebDriver,
    u'webviewapp': WebViewAppDriver,

    # desktop browsers
    u'desktop-chrome': DesktopChromeWebDriver,
    u'desktop-firefox': DesktopFirefoxWebDriver,
    u'desktop-ie': DesktopInternetExplorerWebDriver
}

# all the android versions that appium doesn't support natively. these have to
# use selendroid
SelendroidVersions = [
    u'2.3',
    u'3.0',
    u'3.1',
    u'3.2',
    u'4.0',
    u'4.1',
    # at time writing, appium 1.x lost support for some things that make test
    # writing easier. like find by link text or partial link text. i like those
    # so im making everything use selendroid. seems to work fine so far.
    # plus appium tries to do fancy chromedriver stuff for native webviews. prob
    # a bug but i dont want to deal with it right now.
    u'4.2',
    u'4.3',
    u'4.4',
]


def webdriver_me(os_ver, os_type, app_path=u'', device_type=u''):
    """
    returns a ref to the class that matches for the given os and device type

    :param os_ver: version of the os
    :param os_type: device... type. like android/selendroid/ipad/ios/etc
    :param app_path: the path to the application to be installed, or a browser name
    :param device_type: the type of device ('phone' or 'tablet')
    """
    # ensure these aren't none so we can work with them as strings
    if not os_ver:
        os_ver = u''
    if not os_type:
        os_type = u''
    if not app_path:
        app_path = u''
    if not device_type:
        device_type = u''

    # start off vague with the os type, and hone in on a specific driver if one exists
    driver_type = os_type.lower()

    if os_ver in SelendroidVersions and driver_type == u'android' and not app_path.lower() == u'chrome':
        driver_type = u'selendroid'
    elif driver_type == u'kindle':
        driver_type = u'android'
    elif os_type.lower() == u'linux' or os_type.lower() == u'osx' or os_type.lower() == u'windows':
        if app_path.lower() == u'chrome':
            driver_type = u'desktop-chrome'
        elif app_path.lower() == u'firefox':
            driver_type = u'desktop-firefox'
        elif app_path.lower() == u'ie' or app_path.lower() == u'internet explorer':
            driver_type = u'desktop-ie'
    elif app_path.lower() == u'chrome':
        driver_type = u'chrome'
    elif u'webviewapp' in app_path.lower():
        driver_type = u'webviewapp'

    if driver_type in HackedDrivers:
        log.debug(u'using driver_type "{}" for driver_type "{}" with os_type "{}" and app_path "{}"'.format(HackedDrivers[driver_type], driver_type, os_type, app_path))
        return HackedDrivers[driver_type]
    else:
        log.warning(u'could not find a specific webdriver for {}. using default'.format(driver_type))
        return HackedWebDriver
