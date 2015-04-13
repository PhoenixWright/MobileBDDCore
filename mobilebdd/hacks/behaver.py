"""
overloaded hacks for behave stuff
"""

import logging

from behave.formatter import formatters
from behave.runner_util import parse_features
from behave.model import Step, FileLocation
from behave.runner import Context, os, Runner

import mobilebdd


log = logging.getLogger(u'mobilebdd')


class HackedContext(Context):
    """
    overloaded behave context runner to add our own stuff

    this just adds fields to the object. it's not necessary, but it does make
    it easier to use when coding in an ide (auto completion)

    @type driver: HackedWebDriver
    """

    def __init__(self, runner):
        super(HackedContext, self).__init__(runner)

        # path to the app
        self.app_uri = None

        # app package, for android
        self.app_package = None

        # app activity name, for android
        self.app_activity = None

        # device type, 'phone' or 'tablet' (or None for desktop)
        self.device_type = None

        #the webdriver to use, most likely the HackedWebDriver or child of
        self.driver = None

        # mark whether or not we're using a feature-level driver
        self.feature_driver = False
        
        # os version
        self.os_ver = None

        # os type
        self.os_type = None

        # this flag can tell steps whether or not to re-create the driver
        # object
        # ideally the driver is created in the before_feature hook rather
        # than being created every scenario
        self.refresh_driver = False
       
        # context-specific test data
        self.saved_data = dict()
        
        # the current report directory path for saving test artifacts like
        # screenshots
        self.test_report_dir = None

        # user-specified processor for refining webdriver capabilities
        self.webdriver_processor = None

        # url to hit for webdriver nodes/grids
        self.webdriver_url = None

        if runner.test_config:
            self.test_config = runner.test_config
        else:
            self.test_config = []

    def run_steps(self, steps):
        """
        simple wrapper that makes calling behave's 'execute_steps' easier.

        primarily, meaning that i dont have to use unicode strings, which are
        annoying to type.

        Note! if you're using a non english language, then you should use unicode.

        @steps: string of bdd steps to run
        """
        self.execute_steps(unicode(steps))


class HackedRunner(Runner):
    def __init__(self, config, feature_paths, step_paths, webdriver_processor=None, listeners=None, test_config=None):
        """
        :param feature_paths: list of paths to load feature files from
        :param step_paths: list of paths to load step files from
        """
        super(HackedRunner, self).__init__(config)

        # list of feature dirs to load features from
        self.feature_paths = feature_paths

        # list of paths to load steps from
        self.step_paths = step_paths

        # webdriver url to hit
        self.webdriver_url = None

        # setup base dir in advance so we can call load_step_definitions. this
        # is normally called by run, which we may not want to do all the time,
        # for example when just getting list of known steps
        self.base_dir = mobilebdd.__path__[0]

        # the class users can specify to override things like capabilities
        self.webdriver_processor = webdriver_processor

        # the list of listeners to notify of Behave hook events
        self.listeners = listeners

        self.test_config = test_config

    def setup_paths(self):
        """
        overloading the functionality of behave's path loader because it's very
        limited.

        features and steps must be in the same directory. to be extensible, we
        want to allow steps from different places/modules/packages and features
        in different places (or even dynamically generated).

        this needs to setup:
        self.base_dir - really only used to load environment.py for hooks
            but this is already done in the constructor
        self.config.base_dir - just point to self.base_dir, used by junit reporter
        """
        self.config.base_dir = self.base_dir

    def feature_locations(self):
        """
        overloading this to just specify our own list of feature paths
        """
        log.debug(u'feature_locations')
        log.debug(u'feature paths: {}'.format(self.feature_paths))
        locations = []
        for feature_path in self.feature_paths:
            for current_dir, dirnames, filenames in os.walk(feature_path):
                log.debug(u'feature loading, in path {}'.format(current_dir))
                for filename in sorted(filenames):
                    if filename.endswith(u'.feature'):
                        log.debug(u'feature loading, found: {}'.format(filename))
                        locations.append(FileLocation(os.path.join(current_dir, filename)))
        log.debug(u'end feature_locations')
        return locations

    def load_step_definitions(self, extra_step_paths=None):
        """
        overloading this to allow recursive step file loading and to allow step
        file loading from multiple, unrelated paths

        :param extra_step_paths: this was never used in the behave code. we have
            the instance var of list of steps so ignore this
        """
        # pull all steps recursively
        all_paths = []
        for path_dir in self.step_paths:
            # append the path itself, then recurse into it
            all_paths.append(path_dir)

            for current_dir, subdirs, files in os.walk(path_dir):
                log.debug(u'step path loading, in path {}'.format(current_dir))
                if not subdirs:
                    log.debug(u'skipping {} because there are no subdirs'.format(current_dir))
                    continue
                all_paths += [os.path.join(current_dir, subdir) for subdir in subdirs]
        paths = all_paths

        log.debug(u'final list of step paths: {}'.format(paths))

        super(HackedRunner, self).load_step_definitions(extra_step_paths=paths)

    def run_with_paths(self):
        """
        overloading this so i can use HackedContext
        """
        self.context = HackedContext(self)
        self.context.listeners = self.listeners
        self.context.webdriver_url = self.webdriver_url
        self.context.webdriver_processor = self.webdriver_processor
        self.load_hooks()
        self.load_step_definitions()

        # -- ENSURE: context.execute_steps() works in weird cases (hooks, ...)
        # self.setup_capture()
        # self.run_hook('before_all', self.context)

        # -- STEP: Parse all feature files (by using their file location).
        feature_locations = [filename for filename in self.feature_locations()
                             if not self.config.exclude(filename)]
        features = parse_features(feature_locations, language=self.config.lang)
        self.features.extend(features)

        # -- STEP: Run all features.
        stream_openers = self.config.outputs
        self.formatters = formatters.get_formatter(self.config, stream_openers)
        return self.run_model()


class HackedStep(Step):
    """
    overloaded behave step object so we can add our own stuff

    this just adds fields to the object. it's not necessary, but it does make
    it easier to use when coding in an ide (auto completion)

    this will be used in the after-step listener callback
    """
    def __init__(self, filename, line, keyword, step_type, name, text=None,
                 table=None):
        super(HackedStep, self).__init__(filename, line, keyword, step_type, name, text=text, table=table)

        # file path to the screenshot that was taken after this step was run
        self.screenshot_path = None
        '''
        :ivar: path to the screenshot that was generated for this step, if avail
        :type: string
        '''

        self.start_time_epoch_sec = 0
        '''
        :ivar: unix epoch seconds when this step was started
        :type: float
        '''

        self.end_time_epoch_sec = 0
        '''
        :ivar: unix epoch seconds when this step was completed
        :type: float
        '''
