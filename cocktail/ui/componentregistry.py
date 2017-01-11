#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from pkg_resources import resource_filename
from threading import RLock
from .component import Component


class ComponentRegistry(object):

    file_extension = ".ui"
    auto_reload = True

    def __init__(self):
        self.__components = {}
        self.__lock = RLock()

    def get(self, full_name):

        already_existed = True

        try:
            component = self.__components[full_name]
        except KeyError:
            with self.__lock:
                try:
                    component = self.__components[full_name]
                except KeyError:
                    already_existed = False
                    component = Component(self, full_name)
                    self.__components[full_name] = component
                    component.load()

        if self.auto_reload:
            for dep in component.dependencies(include_self = already_existed):
                if dep.needs_update():
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

