#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from cocktail.html import resource_repositories, StyleSheet


class Theme(object):
    """A singular visual theme for an application.

    The `Theme` makes it possible to inject stylesheets into the shadow DOM of
    components. The theme is chosen when a component is compiled
    """

    def __init__(self, locations, extensions = (".scss", ".css")):
        self.__locations = map(self._normalize_location, locations)
        self.__extensions = map(self._normalize_extension, extensions)

    @property
    def locations(self):
        """Repository locations that the theme will inspect in search of
        stylesheets.

        :return: str list
        """
        return self.__locations

    def _normalize_location(self, location):
        return location.strip().rstrip("/") + "/"

    def add_location(self, location):
        """Add a new location that the theme should consider when looking for
        stylesheets.

        The added location will be given precedence over any existing location.

        :param location: The location to add.
        :type location: str
        """
        self.__locations.insert(0, self._normalize_location(location))

    @property
    def extensions(self):
        """File extensions that the theme will consider when searching
        stylesheets.

        :type: str list
        """
        return self.__extensions

    def _normalize_extension(self, extension):
        return "." + extension.strip().lstrip(".")

    def add_extension(self, extension):
        """Add a new file extension that the theme should consider when
        searching for stylesheets.

        :param extension: The file extension to add.
        :type extension: str
        """
        self.__extensions.insert(0, extension)

    def get_stylesheet(self, component, element_id = None):
        """Get the stylesheet that applies to the given component / part.

        :param component: The component to get the stylesheet for.
        :type component: `cocktail.ui.component.Component`

        :param element_id: The ID of an element within the given component.
            Will be None when looking for stylesheets for the whole component.
        :type element_id: str

        :return: The stylesheet that should be applied to the given component
            or element, or None if no matching stylesheet can be found.
        :rtype: `cocktail.html.resources.StyleSheet` or None
        """
        for uri in self.iter_potential_stylesheets(component, element_id):
            location = resource_repositories.locate(uri)
            if location and os.path.exists(location):
                if not uri.endswith(".css"):
                    uri += ".css"
                return StyleSheet(uri)

        return None

    def iter_potential_stylesheets(self, component, element_id = None):
        """Produces a list of URLs that would apply to the given component /
        part, if they exist.

        :param component: The component to get the stylesheets for.
        :type component: `cocktail.ui.component.Component`

        :param element_id: The ID of an element within the given component.
            Will be None when looking for stylesheets for the whole component.
        :type element_id: str

        :return: An iterable sequence of stylesheets that would apply to the
            given component or element.
        :rtype: str iterable
        """
        name = component.full_name.lower().replace(".", "-")
        if element_id:
            name += "--" + element_id.lower()

        for location in self.__locations:
            for extension in self.extensions:
                yield location + name + extension


default_theme = Theme(["cocktail.ui://styles/"])

