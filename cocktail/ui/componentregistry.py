#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from pkg_resources import resource_filename
from threading import RLock
from .component import Component
from .theme import default_theme
from .exceptions import ComponentFileError


class ComponentRegistry(object):

    file_extension = ".ui"
    theme = default_theme
    auto_reload = True

    def __init__(self):
        self.__components = {}
        self.__lock = RLock()

    def get(self, full_name, referrer = None, reference_type = None):

        already_existed = True

        try:
            component = self.__components[full_name]
        except KeyError:
            with self.__lock:
                try:
                    component = self.__components[full_name]
                except KeyError:
                    already_existed = False
                    try:
                        component = Component(self, full_name)
                        self.__components[full_name] = component
                        component.load()
                    except ComponentFileError, e:
                        if e.full_name == full_name:
                            e.referrer = referrer
                            e.reference_type = reference_type
                        raise e

        if self.auto_reload and component.loaded:
            for dep in component.dependencies(include_self = already_existed):
                if dep.loaded and dep.needs_update():
                    dep.load()

        return component

    def get_component_source_file(self, full_name):
        package_name, name = full_name.rsplit(".", 1)
        return resource_filename(
            package_name,
            name.lower() + self.file_extension
        )

    def _subcomponent(self, parent, name):
        full_name = parent.full_name + "." + name
        subcomponent = Component(self, full_name, parent)
        self.__components[full_name] = subcomponent
        return subcomponent

