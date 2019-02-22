#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.pkgutils import resource_filename
from cocktail.html import resource_repositories
from .component import Component
from .componentregistry import ComponentRegistry

resource_repositories.define(
    "cocktail.ui",
    "/resources/cocktail.ui",
    resource_filename("cocktail.ui", "resources")
)

components = ComponentRegistry()

