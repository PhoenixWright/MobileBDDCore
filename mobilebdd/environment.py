"""
turns behaves environment callbacks into a listener dispatcher
"""

import os
import time
from parse import search
import logging

from selenium.common.exceptions import WebDriverException

from mobilebdd.behave_tools import gentrify_scenario_name
from mobilebdd.drivers.drivers import webdriver_me
from mobilebdd.steps.app_states import APP_PACKAGE_STEP, APP_ACTIVITY_STEP, APP_STEPS, DEVICE_STEPS


log = logging.getLogger(u'mobilebdd')


def get_runtime_requirements_from_steps(steps):
    """Returns a json blob containing the following, if it can find them:
    * device_type
    * os_type
    * os_version
    * app_uri
    * app_package
    * app_activity
    :param steps: the steps in the scenario
    :type steps: unicode
    :return dict with whatever info was found
    :rtype dict
    """
    info = dict()

    # get the app package
    result = search(APP_PACKAGE_STEP, steps)
    if result:
        info[u'app_package'] = result.named.get(u'package', None)
        log.debug(u'detected app_package: {}'.format(info[u'app_package']))

    # get the app activity
    result = search(APP_ACTIVITY_STEP, steps)
    if result:
        info[u'app_activity'] = result.named.get(u'activity', None)
        log.debug(u'detected app_activity: {}'.format(info[u'app_activity']))

    # get the os_ver
    for app_step in APP_STEPS:
        result = search(app_step, steps)
        if result:
            info[u'app_uri'] = result.named.get(u'app', None)
            log.debug(u'detected app_uri: {}'.format(info[u'app_uri']))

            # don't run this loop multiple times if we found a result
            break

    # get the os_type and os_ver
    # using reversed() because the steps should be defined from least to most specific in the core
    for device_step in reversed(DEVICE_STEPS):
        result = search(device_step, steps)
        if result:
            info[u'os_type'] = result.named.get(u'os_type', None)
            info[u'os_version'] = result.named.get(u'os_ver', None)
            log.debug(u'detected os_type: "{}" and os_ver: "{}"'.format(info[u'os_type'], info[u'os_version']))

            # handle form factor
            if u'phone' in device_step:
                info[u'device_type'] = u'phone'
            elif u'tablet' in device_step:
                info[u'device_type'] = u'tablet'

            if u'device_type' in info:
                log.debug(u'detected device_type: "{}"'.format(info[u'device_type']))

            # don't run this loop multiple times if we found a result
            break

    return info


def _setup_report_dir(context, dir_name):
    """
    creates a directory for the given dir name by appending it to the current
    report directory path. then sets the context's report dir field to the path

    :param context: behave context
    :type context: HackedContext
    :type dir_name: str
    """
    if not context.config.junit:
        log.debug(u'not setting up output dir because test output not given')
        return

    context.test_output_dirs.append(dir_name)
    report_dir = os.path.join(os.getcwd(), *context.test_output_dirs)

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    context.test_report_dir = report_dir


def __isolate_call(method, *args):
    """
    calls the given method wrapped in a try catch. this helps prevent external
    listener implementations from borking the core execution.

    :param method: to call
    :param args: other params to pass to the method
    """
    try:
        method(*args)
    except Exception as e:
        log.warning(u'calling {} from listener thew an exception {}'.format(
            method,
            e
        ))


def before_all(context):
    # hierarchal list of test dirs that changes as we exec each scenario
    context.test_output_dirs = []

    # setup report directory
    # if the junit output directory is given, then use that as the starting pt
    if context.config.junit:
        context.test_report_dir = context.config.junit_directory
        context.test_output_dirs.append(context.test_report_dir)

    # fire listeners
    for ear in context.listeners:
        __isolate_call(ear.before_all, context)


def before_feature(context, feature):
    _setup_report_dir(context, feature.name)

    # this is a custom tag that maintains a feature-level driver if specified
    if 'single_session' in feature.tags:
        # try to pre-process some of the steps and create the webdriver instance
        # ideally we share this webdriver instance across a set of tests
        # if we ever have app_uri and os_ver and os_type, we can try to create a driver
        # this for loop breaks after one iteration - using feature.walk_scenarios() to expand examples, if any
        log.debug(u'attempting to create an initial driver to re-use across tests')
        for scenario in feature.walk_scenarios():
            steps = [step.name for step in scenario.background_steps]
            steps += [step.name for step in scenario.steps]
            steps = u'\n'.join(steps)

            # pull the required information out of the steps
            info = get_runtime_requirements_from_steps(steps)
            context.app_uri = info.get(u'app_uri', None)
            context.app_package = info.get(u'app_package', None)
            context.app_activity = info.get(u'app_activity', None)
            context.device_type = info.get(u'device_type', None)
            context.os_type = info.get(u'os_type', None)
            context.os_ver = info.get(u'os_version', None)
            break  # only go through the first scenario, because this is at the feature level

        # now create the driver instance if possible
        if context.app_uri and context.os_ver and context.os_type:
            log.debug(u'found driver variables in step text, creating a new feature-level driver')
            driver_class = webdriver_me(context.os_ver, context.os_type, context.app_uri, context.device_type)
            context.driver = driver_class(
                device_type=context.device_type,
                os_ver=context.os_ver,
                os_type=context.os_type,
                app_path=context.app_uri,
                app_package=context.app_package,
                app_activity=context.app_activity,
                webdriver_url=context.webdriver_url,
                webdriver_processor=context.webdriver_processor
            )

            # mark that we're using a feature-level driver
            context.feature_driver = True
        else:
            log.debug(u'failed to detect app_uri: "{}" and os_ver: "{}" and os_type: "{}"'.format(
                context.app_uri,
                context.os_ver,
                context.os_type
            ))

    # fire listeners
    for ear in context.listeners:
        __isolate_call(ear.before_feature, feature)


def before_scenario(context, scenario):
    scenario_name = gentrify_scenario_name(scenario)

    # make a test report directory for each scenario
    _setup_report_dir(context, scenario_name)

    # fire listeners
    for ear in context.listeners:
        __isolate_call(ear.before_scenario, scenario)


def before_step(context, step):
    """
    :type context: HackedContext
    :type step: HackedStep
    """
    step.start_time_epoch_sec = time.time()

    # fire listeners
    for ear in context.listeners:
        __isolate_call(ear.before_step, step)


def after_step(context, step):
    """
    :type context: HackedContext
    :type step: HackedStep
    """
    step.end_time_epoch_sec = time.time()

    # take screenshot after each step
    # but only if the output dir is given
    if context.config.junit:
        screenshot_file_path = None
        if context.driver:
            # check if the step has saved a custom screenshot that it wants reported
            if hasattr(context, u'step_screenshot'):
                log.debug(u"using step's screenshot rather than taking one because step_screenshot was on the context")
                screenshot_file_path = context.driver.get_screenshot_path(
                    path=context.test_report_dir,
                    suffix=step.name
                )
                with open(screenshot_file_path, u'w') as f:
                    f.write(context.step_screenshot)

                # clear the step_screenshot variable
                del context.step_screenshot
            else:
                log.debug(u'taking screenshot after step: "{}"'.format(step.name))
                screenshot_file_path = context.driver.take_screenshot(
                    path=context.test_report_dir,
                    suffix=step.name
                )
                log.debug(u'done taking screenshot, filepath: "{}"'.format(screenshot_file_path))
        step.screenshot_path = screenshot_file_path

    # fire listeners
    for ear in context.listeners:
        __isolate_call(ear.after_step, step)


def after_scenario(context, scenario):
    """
    :type context: HackedContext
    """
    # close the session so the next test can begin immediately
    # if using the --full-reset flag, appium will bork here. but at that point
    # the webdriver session is already closed. so no-op for exception
    try:
        # if a test failed before the webdriver was setup, then this is undef
        if context.driver and not context.feature_driver:
            log.debug(u'step-level driver.quit()')
            context.driver.quit()
            context.driver = None
    except WebDriverException:
        pass

    if context.config.junit:
        context.test_output_dirs.pop()

    # fire listeners
    for ear in context.listeners:
        __isolate_call(ear.after_scenario, scenario)


def after_feature(context, feature):
    if context.config.junit:
        context.test_output_dirs.pop()

    if context.driver and context.feature_driver:
        log.debug(u'feature-level driver.quit()')
        context.driver.quit()
        context.driver = None
        context.feature_driver = False

    # fire listeners
    for ear in context.listeners:
        __isolate_call(ear.after_feature, feature)


def after_all(context):
    for ear in context.listeners:
        __isolate_call(ear.after_all, context)
