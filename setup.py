#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from setuptools import setup, find_packages

setup(
    name = "cocktail",
    version = "0.3.1",
    author = "Whads/Accent SL",
    author_email = "tech@whads.com",
    description = """A tasty mix of python web development utilities.""",
    long_description =
        "Cocktail is the framework used by the Woost CMS. "
        "It offers a selection of packages to ease the development of complex "
        "web applications, with an emphasis on declarative and model driven "
        "programming.",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Environment :: Web Environment :: Buffet",
        "Framework :: ZODB",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Natural Language :: Catalan",
        "Natural Language :: Spanish",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing :: Markup :: HTML"
    ],
    install_requires = [
        "simplejson",
        "ZODB3==3.8",
        "cherrypy>=3",
        "buffet>=1.0",
        "nose",
        "selenium",
        "pyExcelerator"
    ],
    packages = find_packages(),
    include_package_data = True,

    # Cocktail can't yet access view resources (images, style sheets, client
    # side scripts, etc) that are packed inside a zipped egg, so distribution
    # in zipped form is disabled
    zip_safe = False,

    # Make CML templates available to Buffet
    entry_points = {
        "python.templating.engines":
        ["cocktail=cocktail.html.templates.buffetplugin:CocktailBuffetPlugin"],
        "nose.plugins.0.10":
        ["selenium_tester=cocktail.tests.seleniumtester:SeleniumTester"]
    }
)

