# spec for webdriver processors

class WebDriverProcessor(object):
    """Allows outside users to have the final say on things like capabilities
    that are used to instantiate WebDriver.
    """
    def __init__(self):
        pass

    def process_capabilities(self, capabilities):
        """Process capabilities passed in and return the final dict.
        :type capabilities: dict
        :rtype: dict
        """
        pass
