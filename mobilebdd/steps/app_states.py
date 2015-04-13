"""
steps to do setup stuff for tests, like install apps on devices
"""

from behave import *
import logging
from mobilebdd.drivers.drivers import webdriver_me


log = logging.getLogger(u'mobilebdd')


# make these easily accessible for reference in external packages
# list them from least to most specific for the sake of convention
# the variables in these strings are also in get_runtime_requirements_from_steps, update the code there if they change
APP_PACKAGE_STEP = u"the app's package is {package}"
APP_ACTIVITY_STEP = u"the app's activity is {activity}"
APP_STEPS = [
    u'I have {app} installed',
    u'I download the app from {app}',
    u'I download the {app} app'
]

# the variables in these strings are also in get_runtime_requirements_from_steps, update the code there if they change
DEVICE_STEPS = [
    u'I run the app on {os_type} {os_ver}',
    u'I run the app on a {os_type} {os_ver}',
    u'I run the app on an {os_type} {os_ver}',
    u'I run the app on a {os_type} {os_ver} {device_type}',
    u'I run the app on an {os_type} {os_ver} {device_type}',
]


@given(APP_STEPS[0])
@given(APP_STEPS[1])
@given(APP_STEPS[2])
def _step(context, app):
    """
    :type context: HackedContext
    """
    if context.app_uri != app:
        context.app_uri = app
        context.refresh_driver = True

    if u'app_urls' in context.test_config and app in context.test_config[u'app_urls']:
        context.app_uri = context.test_config[u'app_urls'][app]

    assert context.app_uri, u'a path to the app or a lookup in the test config was not found!'



@given(APP_PACKAGE_STEP)
def _step(context, package):
    """
    :type context: HackedContext
    """
    context.app_package = package


@given(APP_ACTIVITY_STEP)
def _step(context, activity):
    """
    :type context: HackedContext
    """
    context.app_activity = activity


@given(u"the app's user agent is {user_agent}")
def _step(context, user_agent):
    """
    :type context: HackedContext
    """
    context.user_agent = user_agent


@given(u"the app's window size is {window_size_x} by {window_size_y}")
def _step(context, window_size_x, window_size_y):
    """
    :type context: HackedContext
    """
    context.window_size_x = window_size_x
    context.window_size_y = window_size_y


@given(DEVICE_STEPS[0])
@given(DEVICE_STEPS[1])
@given(DEVICE_STEPS[2])
@given(DEVICE_STEPS[3])
@given(DEVICE_STEPS[4])
def _step(context, os_type, os_ver, device_type=None):
    """
    :type context: HackedContext
    """
    user_agent = None
    if hasattr(context, u'user_agent'):
        user_agent = context.user_agent

    window_size_x = None
    if hasattr(context, u'window_size_x'):
        window_size_x = context.window_size_x

    window_size_y = None
    if hasattr(context, u'window_size_y'):
        window_size_y = context.window_size_y

    # validate device type, if it is anything other than phone or tablet do nothing
    if device_type not in [u'phone', u'tablet']:
        device_type = None

    # check if we need to create a new driver (if the os_type or os_ver is different)
    if context.os_type != os_type or context.os_ver != os_ver or context.device_type != device_type:
        context.os_type = os_type
        context.os_ver = os_ver
        context.device_type = device_type
        context.refresh_driver = True

    # check if one of the above steps marked that we should refresh the driver
    if context.driver and not context.refresh_driver:
        log.debug(u'context already has a driver instance and refresh_driver=False, not instantiating one')
    else:
        log.debug(u'creating a new step-level webdriver instance')

        # close the old driver if it exists
        if context.driver:
            try:
                context.driver.quit()
            except Exception as e:
                log.warn(u'error when calling driver.quit(): {}'.format(unicode(e)))

        assert context.app_uri, u'a path to the app wasnt given!'

        # use special/hacked webdrivers based on the os ver/type
        driver_class = webdriver_me(context.os_ver, context.os_type, context.app_uri, context.device_type)
        context.driver = driver_class(
            device_type=context.device_type,
            os_ver=context.os_ver,
            os_type=context.os_type,
            app_path=context.app_uri,
            app_package=context.app_package,
            app_activity=context.app_activity,
            user_agent=user_agent,
            window_size_x=window_size_x,
            window_size_y=window_size_y,
            webdriver_url=context.webdriver_url,
            webdriver_processor=context.webdriver_processor
        )

        # state that we shouldn't refresh the driver unless another step says otherwise
        context.refresh_driver = False

        # mark that we're not using a feature-level driver
        context.feature_driver = False


@step(u'I take a screenshot')
def _step(context):
    """
    :type context: HackedContext
    """
    # we actually dont need to do anything here because screenshots are taken
    # after every step. but this might be something that is more intuitive to
    # users
    pass
