#-*- coding: utf-8 -*-
"""
A plugin that integrates Selenium with the Nose testing framework.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
import os
import socket
from time import time, sleep
from urlparse import urlparse
from cocktail.modeling import wrap
from nose.plugins import Plugin
from selenium import selenium as SeleniumSession

SITE_PORT_RANGE = (1025, 9000)

_selenium_site_address = None
_selenium_sessions = []
_current_selenium_session = None

def get_selenium_enabled():
    return _selenium_site_address is not None

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
        if key in ("jquery_html", "jquery_count", "wait_for_element_present"):
            return object.__getattribute__(self, key)
        else:
            return getattr(_current_selenium_session, key)

    def jquery_html(self, selector):
        return _current_selenium_session \
            .get_eval("window.jQuery('%s').html()" % selector)

    def jquery_count(self, selector):
        return int(
            _current_selenium_session
            .get_eval("window.jQuery('%s').length" % selector)
        )

    def wait_for_element_present(self, locator, timeout, interval = 0.1):
        start = time()
        while not self.is_element_present(locator):
            time_span= time() - start
            if time_span > timeout:
                raise Exception("Timed out after %.2f seconds" % time_span)
            else:
                sleep(interval)

browser = SeleniumSessionProxy()


class SeleniumTester(Plugin):

    def options(self, parser, env = os.environ):

        Plugin.options(self, parser, env)

        parser.add_option("--selenium-host",
            default = "127.0.0.1",
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
        and options.selenium_browsers:
        
            if options.selenium_url:
                selenium_url = options.selenium_url
                url = urlparse(selenium_url)
                _selenium_site_address = url.hostname, url.port or 80
            else:
                _selenium_site_address = (
                    self._get_default_site_address(options.selenium_host)
                )
                selenium_url = "http://%s:%d" % _selenium_site_address

            for browser_command in options.selenium_browsers.split(","):
                session = SeleniumSession(
                    options.selenium_host,
                    options.selenium_port,
                    browser_command,
                    selenium_url
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

    def _get_default_site_address(self, selenium_host):
        
        # Get the local host's IP address, as seen from the selenium server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((selenium_host, 0))
        site_host = s.getsockname()[0]
        s.close()
        
        # Find the first available port on the local host
        site_port = self._find_free_port(SITE_PORT_RANGE)

        return (site_host, site_port)

    def _find_free_port(self, port_range):
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = "0.0.0.0"
        
        for port in port_range:
            try:
                s.bind((host, port))
            except:
                pass
            else:
                s.close()
                return port

        raise IOError("Can't find a free port "
                      "to launch a site to host selenium tests")

