from behave import *
import logging
log = logging.getLogger(u'mobilebdd')


def get_value(context, element, attr, index = None):
    item = context.driver.simple_find(element)
    assert item, u"couldn't find {}".format(element)
    value = getattr(item, attr, None)
    assert value, u"couldn't find attribute {} on {}".format(attr, element)
    if index == None:
        return value
    else:
        return value[index]


def get_key(element, attr, index = None):
    if index == None:
        return element + "__" + attr
    else:
        return element + "__" + attr + "[" + index + "]"


def save_data(context, element, attr, index = None):
    value = get_value(context, element, attr, index)
    attribute_key = get_key(element, attr, index)
    log.debug(u'saving {} to saved_data[{}]'.format(value, attribute_key))
    context.saved_data[attribute_key] = value


def get_saved_value(context, stored_element, stored_attr, index = None):
    stored_key = get_key(stored_element, stored_attr, index)
    assert stored_key in context.saved_data, u'{} was not previously stored'.format(stored_key)

    return context.saved_data[stored_key]


@step(u'I note the {attr} of {element}')
@step(u'I note the {index} index of the {attr} of {element}')
def _step(context, attr, element, index = None):
    """
    :type context: HackedContext
    """

    attribute = get_value(context, element, attr, index)
    attribute_key = get_key(element, attr, index)
    log.debug(u'saving {} to saved_data[{}]'.format(attribute, attribute_key))
    context.saved_data[attribute_key] = attribute


@step(u'the stored {stored_attr} of {stored_element} should match the current {current_attr} of {current_element}')
@step(u'the current {current_attr} of {current_element} should match the stored {stored_attr} of {stored_element}')
@step(u'the current {current_attr} of {current_element} should match its stored value')
@step(u'the stored {stored_attr} of {stored_element} should match the current {current_index} index of the {current_attr} of {current_element}')
def _step(context, current_attr, current_element, stored_attr = None, stored_element = None, current_index = None):
    """
    :type context: HackedContext
    """
    if stored_element is None:
        stored_element = current_element
        
    if stored_attr is None:
        stored_attr = current_attr

    stored_value = get_saved_value(context, stored_element, stored_attr)
    
    current_value = get_value(context, current_element, current_attr, current_index)
    assert current_value == stored_value
