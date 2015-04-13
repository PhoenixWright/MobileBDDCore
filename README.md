# MobileBDDCore

MobileBDDCore is a wrapper around [Behave](http://pythonhosted.org/behave/). It offers a set of BDD steps that handle:

* Instantiating WebDriver against a desktop browser or mobile application via Appium
* Finding elements in HTML
* Tapping elements
* Confirming visibility of elements
* Navigating to URLs and Android activities
* Adding and deleting cookies
* Executing javascript
* Taking screenshots (which happens automatically as well)

...and much more! In addition, it's possible to provide MobileBDDCore with your own BDD step implementations from your own test package, and implement your own hooks at every key step of the test process for custom functionality. Essentially, it provides the test runner and some starter BDD steps, and lets you build whatever you need on top.


## Reporting

MobileBDDCore provides a way to specify your test output directory. If you do, it will export a simple index.html file and folder full of screenshots of every BDD step in your tests for review. In addition, there is a plugin for reporting results to TestRail for every test case - see the plugin tags section for more information.


## Supported Tags


### Feature Level Tags

@single_session - attempts to maintain a single webdriver session for an entire feature if possible
