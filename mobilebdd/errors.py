"""
exceptions/errors that the bdd core might throw

this is in addition to the stuff that behave might throw
"""


class UndefinedStepsError(Exception):
    """
    indicates that there were some steps that were undefined

    the message will provide the list of steps that were missing
    """
    def __init__(self, undef_steps, *args, **kwargs):
        """
        :param undef_steps: list of undefined steps
        :type undef_steps: list[Step]
        """
        self.undef_steps = undef_steps

        message = u'the following steps are not defined, please either define ' \
                  u'them and pass the bdd core the location to your step files ' \
                  u'or ask the owner of the package(s)/service(s) to implement ' \
                  u'them:\n'
        for step in undef_steps:
            message += u'{} {}\n'.format(
                step.step_type, step.name
            )

        super(UndefinedStepsError, self).__init__(message, *args, **kwargs)
