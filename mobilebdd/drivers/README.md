Put extensions of the HackedWebDriver in here.

Some example use cases:

- iOS 7 broke swipe functionality, need to use scroll. Use single 'swipe' abstraction
- Selendroid also doesn't support Appium's swipe function.
- Typing on Selendroid needs special stuff. (wow)

If you add a new WebDriver class, be sure to map it somehow in the HackedDrivers
dict in drivers.py
