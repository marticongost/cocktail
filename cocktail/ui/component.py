#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from json import dumps
from cocktail.modeling import OrderedSet
from cocktail.translations import translations
from cocktail.html import (
    HTMLDocument,
    DocumentMetadata,
    Element,
    Script
)
from .componentloader import ComponentLoader


class Component(object):

    __state = None
    __registry = None
    __full_name = None
    __package_name = None
    __name = None
    __css_class = None
    __parent = None
    __source_file = None

    def __init__(self, registry, full_name, parent = None):
        self.__registry = registry
        self.__full_name = full_name
        self.__css_class = full_name.replace(".", "-")
        self.__package_name, self.__name = full_name.rsplit(".", 1)
        if parent:
            self.__parent = parent
            self.__source_file = parent.__source_file
        else:
            self.__source_file = registry.get_component_source_file(full_name)

    def __repr__(self):
        return "%s <%s>" % (self.__class__.__name__, self.__full_name)

    @property
    def registry(self):
        return self.__registry

    @property
    def name(self):
        return self.__name

    @property
    def package_name(self):
        return self.__package_name

    @property
    def full_name(self):
        return self.__full_name

    @property
    def css_class(self):
        return self.__css_class

    @property
    def timestamp(self):
        return self.__state and self.__state.timestamp

    def needs_update(self):
        timestamp = self.timestamp
        return (
            not timestamp
            or os.stat(self.__source_file).st_mtime > timestamp
        )

    @property
    def source_file(self):
        return self.__source_file

    def get_source(self):
        if self.__state:
            return unicode(self.__state.source)
        else:
            return u""

    @property
    def is_module(self):
        if self.__state:
            return self.__state.is_module
        else:
            return False

    @property
    def base_component(self):
        if self.__state:
            return self.__state.base_component
        else:
            return None

    def dependencies(self, recursive = True, include_self = False):

        dependencies = OrderedSet()

        if self.__state:
            if self.__state.base_component:
                if recursive:
                    dependencies.extend(
                        self.__state.base_component.dependencies(
                            include_self = True
                        )
                    )
                else:
                    dependencies.append(self.__state.base_component)

            if recursive:
                for dep in self.__state.dependencies:
                    dependencies.extend(dep.dependencies(include_self = True))
            else:
                dependencies.extend(self.__state.dependencies)

        if include_self:
            dependencies.append(self)

            subcomponents = self.__state.subcomponents.itervalues()
            if recursive:
                for subcomponent in subcomponents:
                    dependencies.extend(
                        subcomponent.dependencies(include_self = True)
                    )
            else:
                dependencies.extend(subcomponents)

        return dependencies

    @property
    def parent(self):
        return self.__parent

    @property
    def subcomponents(self):
        if self.__state:
            return self.__state.subcomponents
        else:
            return {}

    @property
    def resources(self):
        if self.__state:
            return self.__state.resources
        else:
            return OrderedSet()

    @property
    def translation_keys(self):
        if self.__state:
            return self.__state.translation_keys
        else:
            return set()

    def load(self, node = None):
        prev_state = self.__state
        self.__state = ComponentLoader(self, node)
        if prev_state:
            prev_state.dispose()

    def render_page(self):
        document = self.create_html_document()
        return document.render(collect_metadata = False)

    def create_html_document(self):
        document = HTMLDocument()
        document.metadata = DocumentMetadata()
        document.metadata.resources.append(UIScript(self))
        return document


class UIScript(Script):

    def __init__(self, root_component):
        Script.__init__(
            self,
            "cocktail.ui://scripts/ui.js",
            mime_type = "text/javascript"
        )
        self.root_component = root_component

    def link(self, document, url_processor = None):
        Script.link(self, document, url_processor = url_processor)
        self._embed_components(document)

    def embed(self, document, source):
        Script.embed(self, document, source)
        self._embed_components(document)

    def _embed_components(self, document):

        translation_keys = set()
        translation_prefixes = set()
        components_script = Element("script", type = "text/javascript")

        # Collect all the required components
        for component in self.root_component.dependencies(include_self = True):
            components_script.append(component.get_source())
            document.metadata.resources.extend(component.resources)

            for trans_key in component.translation_keys:
                if trans_key.endswith(".*"):
                    translation_prefixes.add(trans_key[:-1])
                else:
                    translation_keys.add(trans_key)

        if translation_prefixes:
            for trans_key in translations.definitions:
                for prefix in translation_prefixes:
                    if trans_key.startswith(prefix):
                        translation_keys.add(trans_key)
                        break

        # Export translation keys
        if translation_keys:

            trans_map = {}
            for trans_key in translation_keys:
                trans_value = translations(trans_key)
                if trans_value:
                    trans_map[trans_key] = trans_value

            components_script.append(
                "cocktail.ui.translations = %s;" % dumps(trans_map)
            )

        document.scripts_container.append(components_script)

        # Instantiate the root component
        instantiation_script = Element(
            "script",
            type = "text/javascript",
            children = [
                """
                cocktail.ui.root = %s();
                document.body.appendChild(cocktail.ui.root);
                """
                % self.root_component.full_name
            ]
        )
        document.body.append(instantiation_script)

