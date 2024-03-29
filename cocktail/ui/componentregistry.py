#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from threading import RLock
from collections import defaultdict
from cocktail.pkgutils import resource_filename
from .component import Component
from .theme import default_theme
from .exceptions import ComponentFileError


class ComponentRegistry(object):

    file_extension = ".ui"
    theme = default_theme
    auto_reload = True

    def __init__(self):
        self.__components = {}
        self.__overlays = defaultdict(list)
        self.__lock = RLock()

    def resolve(self, component):
        if isinstance(component, str):
            return self.get(component)
        else:
            return component

    def get(self, full_name, referrer = None, reference_type = None):

        already_existed = True
        component = None

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
                    except ComponentFileError as e:
                        # Component file not found; it may be defined as a
                        # subcomponent. Attempt to load its parent component
                        # first, recursively.
                        parent_name, child_name = full_name.rsplit(".", 1)
                        if "." in parent_name:
                            try:
                                parent = self.get(parent_name)
                            except ComponentFileError:
                                pass
                            else:
                                component = parent.subcomponents.get(child_name)

                        if component is None:
                            e.referrer = referrer
                            e.reference_type = reference_type
                            raise e
                    else:
                        self.__components[full_name] = component
                        component.load()

        if not referrer and self.auto_reload and component.loaded:
            for dep in list(
                component.dependencies(include_self = already_existed)
            ):
                if dep.parent is None and dep.loaded and dep.needs_update():
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
        try:
            return self.__components[full_name]
        except KeyError:
            with self.__lock:
                try:
                    return self.__components[full_name]
                except KeyError:
                    subcomponent = Component(self, full_name, parent)
                    self.__components[full_name] = subcomponent
                    return subcomponent

    def get_overlays(self, component_name):
        return self.__overlays.get(component_name) or []

    def add_overlay(self, component_name, overlay_name):
        with self.__lock:
            self.__overlays[component_name].append(overlay_name)
            component = self.__components.get(component_name)
            if component:
                component.load()

