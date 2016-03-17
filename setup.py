#-*- coding: utf-8 -*-
u"""
@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         December 2008
"""
import sys
from setuptools import setup, find_packages

setup(
    name = "cocktail",
    version = "1.8.3",
    author = "Whads/Accent SL",
    author_email = "tech@whads.com",
    description = """A tasty mix of python web development utilities.""",
    long_description =
        "Cocktail is the framework used by the Woost CMS. "
        "It offers a selection of packages to ease the development of complex "
        "web applications, with an emphasis on declarative and model driven "
        "programming.",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: ZODB",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing :: Markup :: HTML"
    ],
    install_requires = [
        "frozendict",
        "simplejson",
        "transaction==1.1.1",
        "ZODB3==3.10.5",
        "zodbupdate",
        "zope.index==3.6.1",
        "cherrypy==3.1.2",
        "buffet>=1.0",
        "nose",
        "selenium",
        "pyExcelerator",
        "Beaker",
        "BeautifulSoup4",
        "lxml",
        "httplib2",
        "PyStemmer"
    ],
    extras_require = {
        "sass": ["libsass"]
    },
    packages = find_packages(),
    include_package_data = True,

    # Cocktail can't yet access view resources (images, style sheets, client
    # side scripts, etc) that are packed inside a zipped egg, so distribution
    # in zipped form is disabled
    zip_safe = False,

    entry_points = {
        "python.templating.engines":
        ["cocktail=cocktail.html.templates.buffetplugin:CocktailBuffetPlugin"],
        "nose.plugins.0.10":
        ["selenium_tester=cocktail.tests.seleniumtester:SeleniumTester"]
    }
)

