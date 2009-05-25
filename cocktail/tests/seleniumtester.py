#-*- coding: utf-8 -*-
"""
A plugin that integrates Selenium with the Nose testing framework.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
import os
from urlparse import urlparse
from cocktail.modeling import wrap
from nose.plugins import Plugin
from selenium import selenium as SeleniumSession

_selenium_site_address = None
_selenium_sessions = []
_current_selenium_session = None

def get_selenium_site_address():
    return _selenium_site_address

def selenium_test(func):

    def wrapper(*args):
        for session in _selenium_sessions:
            yield (_selenium_test_factory(func, session),) + args

    wrap(func, wrapper)
    return wrapper

selenium_test.__test__ = False

def _selenium_test_factory(test_func, session):
    
    def wrapper(*args, **kwargs):
        global _current_selenium_session
        previous_session = _current_selenium_session
        _current_selenium_session = session
        _current_selenium_session.delete_all_visible_cookies()
        try:
            return test_func(*args, **kwargs)
        finally:
            _current_selenium_session = previous_session

    wrap(test_func, wrapper)
    wrapper.description = "%s (%s)" % (
        wrapper.func_name,
        session.browserStartCommand
    )
    return wrapper


class SeleniumSessionProxy(object):

    def __getattribute__(self, key):
        return getattr(_current_selenium_session, key)


browser = SeleniumSessionProxy()


class SeleniumTester(Plugin):

    def options(self, parser, env = os.environ):

        Plugin.options(self, parser, env)

        parser.add_option("--selenium-host",
            default = "localhost",
            help = "The host of the Selenium RC server."
        )

        parser.add_option("--selenium-port",
            default = "4444",
            help = "The port for the Selenium RC server."
        )

        parser.add_option("--selenium-browsers",
            help = "A comma separated list of browser start commands. "
                "Selenium tests will run once for each specified browser."
        )

        parser.add_option("--selenium-url",
            help = "Root URL for selenium tests."
        )
    
    def configure(self, options, conf):

        global _selenium_site_address

        Plugin.configure(self, options, conf)

        if self.enabled \
        and options.selenium_host \
        and options.selenium_port \
        and options.selenium_browsers \
        and options.selenium_url:

            url = urlparse(options.selenium_url)
            _selenium_site_address = url.hostname, url.port or 80
            
            for browser_command in options.selenium_browsers.split(","):
                session = SeleniumSession(
                    options.selenium_host,
                    options.selenium_port,
                    browser_command,
                    options.selenium_url
                )
                _selenium_sessions.append(session)

    def begin(self):
        # Start all browser sessions before testing begins
        for session in _selenium_sessions:
            session.start()

    def finalize(self, result):
        # Close all browsers after all tests have run
        for session in _selenium_sessions:
            session.stop()

