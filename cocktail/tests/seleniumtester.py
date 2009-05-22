#-*- coding: utf-8 -*-
"""
A plugin that integrates Selenium with the Nose testing framework.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
import os
from nose.plugins import Plugin
from selenium import selenium as SeleniumSession

_selenium_sessions = []

def selenium_test(func):

    def wrapper(*args):
        for session in _selenium_sessions:
            yield (func, session) + args

    return wrapper


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

        Plugin.configure(self, options, conf)

        if self.enabled \
        and options.selenium_host \
        and options.selenium_port \
        and options.selenium_browsers \
        and options.selenium_url:

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

    def finalize(self):
        # Close all browsers after all tests have run
        for session in _selenium_sessions:
            session.stop()

