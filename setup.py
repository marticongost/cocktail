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
    version = "2.0a1",
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
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing :: Markup :: HTML"
    ],
    install_requires = [
        "frozendict",
        "ZODB",
        "zodbupdate",
        "zope.index",
        "cherrypy",
        "nose",
        "Beaker",
        "BeautifulSoup4",
        "lxml",
        "httplib2",
        "PyStemmer",
        "rfc6266"
    ],
    extras_require = {
        "sass": ["libsass==0.12.3"]
    },
    packages = find_packages(),
    include_package_data = True,
    # Cocktail can't yet access view resources (images, style sheets, client
    # side scripts, etc) that are packed inside a zipped egg, so distribution
    # in zipped form is disabled
    zip_safe = False,
    entry_points = {
        "python.templating.engines":
        ["cocktail=cocktail.html.templates.buffetplugin:CocktailBuffetPlugin"]
    }
)

