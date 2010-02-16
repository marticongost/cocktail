#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from os import listdir
from os.path import join, isdir
from setuptools import setup, find_packages

def rglob(base, path, patterns):
    composite = []
    for pattern in patterns:
        composite.append(join(path, pattern))
    for name in listdir(join(base, path)):
        if isdir(join(base, path, name)):
            composite.extend(rglob(base, join(path, name), patterns))
    return composite

setup(
    name = "cocktail",
    version = "0.2",
    author = "Whads/Accent SL",
    author_email = "tech@whads.com",
    description = """A tasty mix of python web development utilities.""",
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
    package_data = {
        "cocktail.html": 
            ["*.cml"] + rglob("cocktail/html", "resources/", ["*.*"])
    },

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

