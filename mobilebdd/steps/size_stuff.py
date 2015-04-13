"""
steps to verify sizes of elements
"""

from behave import *
import logging

log = logging.getLogger(u'mobilebdd')


def scaling_factor(context, ruler, rulerWidth):
    """
    :type context: HackedContext
    """

    rulerElement = context.driver.simple_find(ruler)
    rulerPixels = rulerElement.size['width']
    scaleFactor = float(rulerPixels) / float(rulerWidth)

    return scaleFactor


@then(u'{element} size should be {width}x{height} pixels')
def _step(context, element, width, height):
    """
    :type context: HackedContext
    """

    item = context.driver.simple_find(element)
    itemWidth = item.size['width']
    itemHeight = item.size['height']

    assert itemWidth == int(width),\
        u'{} is {} wide. Expected it to be {} wide'.format(element, itemWidth, width)
    assert itemHeight == int(height),\
        u'{} is {} high. Expected it to be {} high'.format(element, itemHeight, height)


@then(u'{element} size should be {width}x{height} dp using {ruler} as ruler at {rulerWidth} dp')
def _step(context, element, width, height, ruler, rulerWidth):
    """
    :type context: HackedContext
    """

    scaleFactor = scaling_factor(context, ruler, rulerWidth)

    item = context.driver.simple_find(element)
    itemWidth = int(item.size['width'] / scaleFactor)
    itemHeight = int(item.size['height'] / scaleFactor)

    assert itemWidth == int(width),\
        u'{} is {} wide. Expected it to be {} wide'.format(element, itemWidth, width)
    assert itemHeight == int(height),\
        u'{} is {} high. Expected it to be {} high'.format(element, itemHeight, height)


@then(u'{element} should be positioned at ({xValue}, {yValue}) pixels')
def _step(context, element, xValue, yValue):
    """
    @type context: HackedContext
    """

    item = context.driver.simple_find(element)
    itemX = item.location['x']
    itemY = item.location['y']

    assert xValue == itemX,\
        u'{} is located at unexpected X Value. Expected = {}, Actual = {}'.format(element, xValue, itemX)
    assert yValue == itemY,\
        u'{} is located ad unexpected Y Value. Expected = {}, Actual = {}'.format(element, yValue, itemY)


@then(u'{element} should be positioned at ({xValue}, {yValue}) dp within {thing} using {ruler} as ruler at {rulerWidth} dp')
def _step(context, element, xValue, yValue, ruler, rulerWidth):
    """
    :type context: HackedContext
    """

    scaleFactor = scaling_factor(context, ruler, rulerWidth)

    thingItem = context.driver.simple_find(element)
    thingX = item.location['x']
    thingY = item.location['y']

    item = context.driver.simple_find(element)
    itemX = int((item.location['x'] - thingX) / scaleFactor)
    itemY = int((item.location['y'] - thingY) / scaleFactor)

    assert int(xValue) == itemX,\
        u'{} is located at unexpected X Value. Expected = {}, Actual = {}'.format(element, xValue, itemX)
    assert int(yValue) == itemY,\
        u'{} is located ad unexpected Y Value. Expected = {}, Actual = {}'.format(element, yValue, itemY)


@then(u'{element} should be positioned at ({xValue}, {yValue}) dp using {ruler} as ruler at {rulerWidth} dp')
def _step(context, element, xValue, yValue, ruler, rulerWidth):
    """
    :type context: HackedContext
    """

    scaleFactor = scaling_factor(context, ruler, rulerWidth)

    item = context.driver.simple_find(element)
    itemX = int(item.location['x'] / scaleFactor)
    itemY = int(item.location['y'] / scaleFactor)

    assert int(xValue) == itemX,\
        u'{} is located at unexpected X Value. Expected = {}, Actual = {}'.format(element, xValue, itemX)
    assert int(yValue) == itemY,\
        u'{} is located ad unexpected Y Value. Expected = {}, Actual = {}'.format(element, yValue, itemY)


@then(u'{element} should be the size of the app')
def _step(context, element):
    """
    :type context: HackedContext
    """

    rootView = context.driver.simple_find("content")
    rootWidth = rootView.size['width']
    rootHeight = rootView.size['height']

    item = context.driver.simple_find(element)
    itemWidth = item.size['width']
    itemHeight = item.size['height']

    assert rootWidth == itemWidth,\
        u'{} width, {}, does not match app width, {}'.format(element, itemWidth, rootWidth)
    assert rootHeight == itemHeight,\
        u'{} height, {}, does not match app height, {}'.format(element, itemHeight, rootHeight)


@then(u'the text in {element} should equal the {dimension} of the app in dp using {ruler} as ruler at {rulerWidth} dp')
def _step(context, element, dimension, ruler, rulerWidth):
    """
    :type context: HackedContext
    """

    scaleFactor = scaling_factor(context, ruler, rulerWidth)

    rootView = context.driver.simple_find("content")
    actualDimension = int(rootView.size[dimension] / scaleFactor)

    item = context.driver.simple_find(element)
    expectedDimension = int(item.text)

    assert expectedDimension == actualDimension,\
        u'{} contains the text "{}" which is not equal to app {},which is {}'.format(element, expectedDimension, dimension, actualDimension)


@then(u'the text in {element} should equal the {dimension} dimension of {thing} in dp using {ruler} as ruler at {rulerWidth} dp')
def _step(context, element, dimension, thing, ruler, rulerWidth):
    """
    :type context: HackedContext
    """

    scaleFactor = scaling_factor(context, ruler, rulerWidth)

    measuredItem = context.driver.simple_find(thing)
    actualDimension = int(measuredItem.size[dimension] / scaleFactor)

    item = context.driver.simple_find(element)
    expectedDimension = int(item.text)

    assert actualDimension == expectedDimension,\
        u'{} contains the text "{}" which is not equal to the {} of {}, which is {}'.format(element, expectedDimension, dimension, thing, actualDimension)


@then(u'the text in {element} should equal the {coordinate} coordinate of {thing} within {otherThing} in dp using {ruler} as ruler at {rulerWidth} dp')
def _step(context, element, coordinate, thing, otherThing, ruler, rulerWidth):
    """
    :type context: HackedContext
    """

    scaleFactor = scaling_factor(context, ruler, rulerWidth)

    measuredItem = context.driver.simple_find(thing)
    itemCoord = measuredItem.location[coordinate]

    otherItem = context.driver.simple_find(otherThing)
    otherItemCoord = otherItem.location[coordinate]

    actualCoord = int((itemCoord - otherItemCoord) / scaleFactor)
    
    item = context.driver.simple_find(element)
    expectedCoord = int(item.text)

    assert actualCoord == expectedCoord,\
        u'{} contains the text "{}" which is not equal to the {} coordinate of {} within {}, which is {}'.format(element, expectedCoord, coordinate, thing, otherThing, actualCoord)


@then(u'the text in {element} should equal the {coordinate} coordinate of {thing} in dp using {ruler} as ruler at {rulerWidth} dp')
def _step(context, element, coordinate, thing, ruler, rulerWidth):
    """
    :type context: HackedContext
    """

    scaleFactor = scaling_factor(context, ruler, rulerWidth)

    measuredItem = context.driver.simple_find(thing)
    actualCoord = int(measuredItem.location[coordinate] / scaleFactor)

    item = context.driver.simple_find(element)
    expectedCoord = int(item.text)

    assert actualCoord == expectedCoord,\
        u'{} contains the text "{}" which is not equal to the {} coordinate of {}, which is {}'.format(element, expectedCoord, coordinate, thing, actualCoord)

