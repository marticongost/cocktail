#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from json import dumps
from cocktail.modeling import OrderedSet
from cocktail.translations import (
    translations,
    get_language,
    translate_locale,
    directionality
)
from cocktail.html import (
    HTMLDocument,
    DocumentMetadata,
    Element,
    Script,
    StyleSheet
)
from .componentloader import ComponentLoader
from .exceptions import ComponentFileError

POLYFILL_URI = "//cdnjs.cloudflare.com/ajax/libs/document-register-element/" \
               "1.4.1/document-register-element.js"

DEFAULT_GLOBAL_STYLE_SHEET = "cocktail.ui://styles/global.scss.css"


class Component(object):

    __state = None
    __registry = None
    __full_name = None
    __package_name = None
    __name = None
    __tag = None
    __css_class = None
    __parent = None
    __source_file = None

    def __init__(self, registry, full_name, parent = None):

        name_with_dashes = full_name.replace(".", "-")

        self.__registry = registry
        self.__full_name = full_name
        self.__tag = name_with_dashes.lower()
        self.__css_class = name_with_dashes
        self.__package_name, self.__name = full_name.rsplit(".", 1)

        if parent:
            self.__parent = parent
            self.__source_file = parent.__source_file
        else:
            try:
                self.__source_file = registry.get_component_source_file(full_name)
            except ImportError:
                raise ComponentFileError(full_name)

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
    def tag(self):
        return self.__tag

    @property
    def css_class(self):
        return self.__css_class

    @property
    def timestamp(self):
        return self.__state and self.__state.timestamp

    def needs_update(self):

        timestamp = self.timestamp
        if not timestamp:
            return True

        try:
            source_timestamp = os.stat(self.__source_file).st_mtime
        except OSError:
            return True

        return source_timestamp > timestamp

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

    def ascend_ancestry(self, include_self = False):

        if include_self:
            yield self

        ancestor = self.base_component
        while ancestor:
            yield ancestor
            ancestor = ancestor.base_component

    def descend_ancestry(self, include_self = False):

        base = self.base_component
        if base:
            for ancestor in base.descend_ancestry(True):
                yield ancestor

        if include_self:
            yield self

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

            if self.__state:
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

    def render_page(
        self,
        title = "",
        locales = None,
        splash = "cocktail.ui.Splash",
        global_style_sheet = DEFAULT_GLOBAL_STYLE_SHEET
    ):
        document = self.create_html_document(
            title = title,
            locales = locales,
            splash = splash,
            global_style_sheet = global_style_sheet
        )
        return document.render(collect_metadata = False)

    def create_html_document(
        self,
        title = "",
        locales = None,
        splash = "cocktail.ui.Splash",
        global_style_sheet = DEFAULT_GLOBAL_STYLE_SHEET
    ):
        document = HTMLDocument()
        document.metadata = DocumentMetadata()
        document.metadata.page_title = title
        document.metadata.resources.append(Script(POLYFILL_URI))
        document.metadata.resources.append(
            UIScript(
                self,
                locales = locales,
                splash = splash,
                global_style_sheet = global_style_sheet
            )
        )
        return document


class UIScript(Script):

    def __init__(
        self,
        root_component,
        locales = None,
        splash = "cocktail.ui.Splash",
        global_style_sheet = DEFAULT_GLOBAL_STYLE_SHEET
    ):
        Script.__init__(
            self,
            "cocktail.ui://scripts/ui.js",
            mime_type = "text/javascript"
        )
        self.root_component = root_component
        self.locales = locales
        self.splash = splash
        self.global_style_sheet = global_style_sheet

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
        dependencies = self.root_component.dependencies(
            include_self = True
        )

        if self.splash:
            dependencies.extend(
                self.root_component.registry
                    .get(self.splash)
                    .dependencies(include_self = True)
            )

        for component in dependencies:
            components_script.append("\n")
            components_script.append(component.get_source())
            document.metadata.resources.extend(
                resource
                for resource in component.resources
                if not isinstance(resource, StyleSheet)
            )

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

        # Global declarations
        locales = self.locales or [get_language()]
        declarations_script = Element("script", type = "text/javascript")
        if self.global_style_sheet:
            declarations_script.append(
                "cocktail.ui.globalStyleSheet = %s;"
                % dumps(self.global_style_sheet)
            )
        declarations_script.append(
            "cocktail.ui.locales = %s;" % dumps(locales)
        )
        declarations_script.append(
            "cocktail.ui.directionality = %s;"
            % dumps(
                dict(
                    (locale, directionality.get(locale))
                    for locale in locales
                )
            )
        )
        document.scripts_container.append(declarations_script)

        # Export translation keys
        if translation_keys or locales:

            trans_map = {}
            for trans_key in translation_keys:
                trans_value = translations(trans_key)
                if trans_value:
                    trans_map[trans_key] = trans_value

            for locale in locales:
                trans_map["cocktail.locales." + locale] = \
                    translate_locale(locale)

            declarations_script.append(
                "cocktail.ui.translations = %s;" % dumps(trans_map)
            )

        components_script.place_after(document.scripts_container)

        # Instantiate the root component
        instantiation_script = Element(
            "script",
            type = "text/javascript",
            children =
                (
                    "cocktail.ui.splash(%s.create(), %s)"
                    % (
                        self.splash,
                        self.root_component.full_name
                    )
                )
                if self.splash else
                (
                    "%s.main(document.body);"
                    % self.root_component.full_name
                )
        )
        document.body.append(instantiation_script)

