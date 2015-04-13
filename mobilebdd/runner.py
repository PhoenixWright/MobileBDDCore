"""
stuff to run behave programmatically
"""
import os
import logging
import json

from behave import step_registry
from behave.configuration import Configuration, ConfigError
from behave.tag_expression import TagExpression
from behave.parser import ParserError
from behave.runner_util import FileNotFoundError,\
    InvalidFileLocationError, InvalidFilenameError

from hacks.behaver import HackedRunner
from mobilebdd.errors import UndefinedStepsError
from reports.html import HtmlReporter


log = logging.getLogger(u'mobilebdd')


# real steps, when behave has a 'step' step type, expand it out to these when
# getting the list of known steps
RealSteps = [u'Given', u'When', u'Then']


def _run_behave(feature_dirs, config, step_dirs=None, webdriver_url=None,
                webdriver_processor=None, listeners=None, test_config=None):
    """
    run behave

    :param feature_dirs: list of directories where the test feature files are
    :type feature_dirs: list[string]
    :param config: configuration for behave
    :type config: Configuration
    :param step_dirs: list of directories to load extra steps from. can just be
        a single path string also
    :type step_dirs: list[string] or string
    :param webdriver_url: url to specify the webdriver node or selenium grid to
        ping when running tests on mobile
    :type webdriver_url: string
    :param webriver_processor: class user specifies to override capabilities
    :type webdriver_processor: WebDriverProcessor
    :param listeners: list of listeners
    :type listeners: list[Listener]

    :return: True if the tests passed, else False
    :rtype: bool

    :raise ParserError: when a feature file couldnt be parsed
    :raise ConfigError: when the configuration for the runner was bad
    :raise FileNotFoundError: when a feature file couldnt be found
    :raise InvalidFileLocationError: when a feature path was bad
    :raise InvalidFilenameError: when a feature file name was bad
    :raise UndefinedStepsError: if some steps were undefined
    """
    # append steps from the bdd core
    if not step_dirs:
        step_dirs = []

    if isinstance(step_dirs, str):
        step_dirs = [step_dirs]
    if not step_dirs.count(os.path.dirname(__file__)):
        step_dirs.append(os.path.dirname(__file__))

    # ensure that the webdriver url is in string format for selenium, which can't support unicode
    if isinstance(webdriver_url, unicode):
        log.debug(u'webdriver_url was specified as unicode, encoding to ascii for selenium module compatibility')
        webdriver_url = webdriver_url.encode(u'ascii', u'ignore')

    if not listeners:
        listeners = []

    runner = HackedRunner(config, feature_dirs, step_dirs, webdriver_processor=webdriver_processor, listeners=listeners, test_config=test_config)
    runner.webdriver_url = webdriver_url

    try:
        failed = runner.run()
    except (ParserError, ConfigError, FileNotFoundError,
            InvalidFileLocationError, InvalidFilenameError) as e:
        log.error(e)
        raise e

    if runner.undefined_steps:
        e = UndefinedStepsError(runner.undefined_steps)
        log.error(e)
        raise e

    return not failed


def goh_behave(feature_dirs=None, step_dirs=None, test_artifact_dir=None,
               listeners=None, dry_run=False, webdriver_url=None,
               webdriver_processor=None, tags=None, show_skipped=True, config_file=None,
               test_config=None):
    """
    runs behave

    :param feature_dirs: list of paths to feature files to run, or a single path. Defaults to singleton list of "features"
    :type feature_dirs: list
    :param step_dirs: list of paths to load steps from. the steps paths will be
        searched recursssssively
    :type step_dirs: list
    :param test_artifact_dir: path to where to store test artifacts. if None, no test
        artifacts will be written. note that setting this to None will prevent
        screenshots from automatically being taken after each step
    :param listeners: list of Listener objects to call for diff pts of the test
    :type listeners: list
    :param dry_run: if True, behave will just check if all steps are defined
    :param webdriver_url: optional. webdriver node/grid url to hit to execute
        tests
    :param webdriver_processor: provides the ability to process things like
        capabilities before they're actually used
    :param config_file: a configuration file, formatted as JSON data, that contains
        all of the other parameters listed here (except for listeners or webdriver_processor)
    :param test_config: a configuration that is a dictionary of the parameters. If a config_file is
        also passed, the values in the config_file will be written to the test_config as well. Any existing
        keys will have the values overwritten by the value in the config_file

    :return: True if the tests passed, else False
    :rtype: bool

    :raise ParserError: when a feature file couldnt be parsed
    :raise FileNotFoundError: when a feature file couldnt be found
    :raise InvalidFileLocationError: when a feature path was bad
    :raise InvalidFilenameError: when a feature file name was bad
    :raise UndefinedStepsError: if some steps were undefined
    """

    if config_file:
        try:
            with open(config_file) as config:
                try:
                    json_config = json.load(config)
                except ValueError as e:
                    raise ValueError(u'Could not parse {} config file as JSON. See sample.config for an example config file. {}'.format(config_file, e))
                if test_config:
                    test_config.update(json_config)
                else:
                    test_config = json_config
        except EnvironmentError as e:
            raise IOError(u'Could not open the {} config file. See sample.config for an example config file. {}'.format(config_file, e))

    if test_config:
        log.debug(u'Using test_config:')
        for key in test_config:
            log.debug(u'    {}: {}'.format(key, test_config[key]))
        if u'feature_dirs' in test_config and not feature_dirs:
            feature_dirs = test_config[u'feature_dirs']
        if u'step_dirs' in test_config and not step_dirs:
            step_dirs = test_config[u'step_dirs']
        if u'test_artifact_dir' in test_config and not test_artifact_dir:
            test_artifact_dir = test_config[u'test_artifact_dir']
        if u'dry_run' in test_config:
            dry_run = test_config[u'dry_run']
        if u'webdriver_url' in test_config and not webdriver_url:
            webdriver_url = test_config[u'webdriver_url']
        if u'tags' in test_config and not tags:
            tags = test_config[u'tags']
        if u'show_skipped' in test_config:
            show_skipped = test_config[u'show_skipped']

    if not feature_dirs:
        feature_dirs = ["features"]
    if isinstance(feature_dirs, basestring):
        feature_dirs = [feature_dirs]

    args = [u'']

    # first run in dry run mode to catch any undefined steps
    # if the user specifies dry run mode, then don't do this, since it'll be
    # done anyway
    # but we're running it always anyway. so what's the difference? if user
    # specifies dry run mode, they might also give listeners, etc.
    # auto dry run mode is meant to happen silently
    if not dry_run:
        config = Configuration([u'--dry-run'])
        config.format = []
        _run_behave(feature_dirs, config, step_dirs=step_dirs)

    # output test artifacts
    if test_artifact_dir:
        args.append(u'--junit')
        args.append(u'--junit-directory')
        args.append(test_artifact_dir)

    if dry_run:
        args.append(u'--dry-run')

    # setup config for behave's runner
    config = Configuration(args)
    config.format = [
        # outputs pretty output in to stdout while tests are running
        u'pretty'
    ]

    # Set the tags if there are any
    if tags:
        log.debug(u'Running Scenarios with Tag(s): {}'.format(tags))
        if isinstance(tags, list):
            log.debug(u'Running Scenarios with Tag List')
            config.tags = TagExpression(tags)
        else:
            config.tags = TagExpression(tags.split())

    config.show_skipped = show_skipped
    if not show_skipped:
        log.debug(u'Not showing skipped scenarios.')

    # only add html reporter if the test artifacts are enabled
    if test_artifact_dir:
        config.reporters.append(HtmlReporter(config, test_artifact_dir))

    try:
        return _run_behave(
            feature_dirs,
            config,
            step_dirs=step_dirs,
            webdriver_url=webdriver_url,
            webdriver_processor=webdriver_processor,
            listeners=listeners,
            test_config = test_config
        )
    except ConfigError as e:
        # since we control the configuration file, we shouldn't expose this to
        # the user, since there's nothing they can do
        log.error(e)
        return False


def get_available_steps(step_dirs=None):
    """
    gets all the steps that the core is aware of. useful for doing real-time
    'syntax' checking for uis

    you dont need to call goh_behave prior

    :param step_dirs: optional. list of dirs to additionally load steps from

    :return: a list of found steps' text
    :rtype: list[string]
    """
    # setup config for behave's runner
    # use dry run so only steps are evaluated, nothing is run
    config = Configuration([u'--dry-run'])
    # i dont want std output about the running test, because there is no test
    # whoa...
    config.format = [u'null']

    # append steps from the bdd core
    if not step_dirs:
        step_dirs = []

    # no features, we just want the implemented steps
    feature_dirs = []
    runner = HackedRunner(config, feature_dirs, step_dirs)

    # this is the key part. this will cause behave to run through all the step
    # dirs and execute them, which will cause steps to be registered.
    runner.load_step_definitions()

    # reach into behave's step registry and serialize the known steps into a list
    found_steps = []
    for steps in step_registry.registry.steps.values():
        for step in steps:
            if step.step_type is None or u'step' == step.step_type:
                for real_key in RealSteps:
                    found_steps.append(u'{} {}'.format(real_key, step.string))
            else:
                found_steps.append(u'{} {}'.format(step.step_type, step.string))
            found_steps.append(u'{} {}'.format(u'And', step.string))

    return found_steps
