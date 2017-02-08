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
    version = "0.1a",
    author = "Whads/Accent SL",
    author_email = "tech@whads.com",
    description = """A tasty mix of python web development utilities.""",
    install_requires = [
        "simplejson",
        "ZODB3==3.8",
        "cherrypy==3.1.2",
        "buffet>=1.0",
        "nose",
        "selenium",
        "Beaker"
    ],
    include_package_data = True,
    packages = find_packages(),

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

