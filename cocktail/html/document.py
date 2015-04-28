#-*- coding: utf-8 -*-
u"""Defines the `HTMLDocument` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from simplejson import dumps
from cocktail.translations import translations, get_language
from cocktail.html.element import Element, Content
from cocktail.html.ieconditionalcomment import IEConditionalComment, IEWrapper
from cocktail.html.resources import Script, StyleSheet
from cocktail.html.rendering import Rendering
from cocktail.html.utils import rendering_html5, rendering_xml
from cocktail.html.documentmetadata import DocumentMetadata

HTTP_EQUIV_KEYS = frozenset((
    "content-type",
    "expires",
    "refresh",
    "set-cookie",
    "x-ua-compatible"
))


class HTMLDocument(Element):
    """An object that creates the document structures used when rendering an
    element as a full page.
    """
    __core_scripts_added = False
    core_scripts = [
        Script("/cocktail/scripts/jquery.js"),
        Script("/cocktail/scripts/core.js")
    ]

    tag = "html"
    styled_class = False
    content = ""
    root_element_id = None
    metadata = DocumentMetadata()
    rendering_options = {}
    ie_html5_workaround = True
    resource_sets = []

    def _render(self, rendering):

        doctype = self.metadata.doctype
        if doctype is None:
            doctype = rendering.renderer.doctype

        if doctype:
            rendering.write(doctype.strip())
            rendering.write("\n")

        Element._render(self, rendering)

    def _build(self):

        self.head = Element("head")
        self.append(self.head)

        self.meta_container = Element(None)
        self.head.append(self.meta_container)

        self.title = Element("title")
        self.title.collapsible = True
        self.head.append(self.title)

        self.resources_container = Element(None)
        self.head.append(self.resources_container)

        self.styles_container = Element(None)
        self.resources_container.append(self.styles_container)

        self.scripts_container = Element(None)
        self.resources_container.append(self.scripts_container)

        self.client_setup = Element("script")
        self.client_setup["type"] = "text/javascript"
        self.head.append(self.client_setup)

        self.client_setup_container = Element(None)
        self.client_setup.append(self.client_setup_container)

        self.body = IEWrapper("body")
        self.append(self.body)

        self.javascript_enabled_script = Element("script")
        self.javascript_enabled_script["type"] = "text/javascript"
        self.javascript_enabled_script.append(
            "document.body.className += ' scripted';"
        )
        self.body.append(self.javascript_enabled_script)

    def _ready(self):

        if rendering_xml():
            self["xmlns"] = "http://www.w3.org/1999/xhtml"

        # Process client models first, to allow their content (which hasn't
        # been rendered yet) to supply metadata to the document
        self._add_client_models()

        self._add_language()
        self._add_meta()
        self._add_title()
        self._add_resources()
        self._add_client_variables()
        self._add_client_translations()
        self._add_content()

        for callback in self.metadata.document_ready_callbacks:
            callback(self)

    def _add_language(self):
        language = self.metadata.language or get_language()
        if language:
            self["lang"] = language
            if rendering_xml():
                self["xml:lang"] = language

    def _add_meta(self):

        # Content type and charset should always go first
        self.content_type_metatag = Element("meta")
        self.content_type_metatag["http-equiv"] = "Content-Type"
        self.content_type_metatag["content"] = "%s; charset=%s" % (
            self.metadata.content_type or "text/html",
            self.metadata.charset or "utf-8"
        )
        self.meta_container.append(self.content_type_metatag)

        # Document-wide default base URL for relative URLs
        if self.metadata.base_href:
            base = Element("base")
            base["href"] = self.metadata.base_href
            self.meta_container.append(base)

        # Other meta tags
        for key, value in self.metadata.meta.iteritems():
            meta = Element("meta")

            if key.lower() in HTTP_EQUIV_KEYS:
                attribute = "http-equiv"
            else:
                attribute = "name"

            meta[attribute] = key
            meta["content"] = value
            self.meta_container.append(meta)

    def _add_title(self):
        if self.metadata.page_title:
            self.title.append(self.metadata.page_title)

    def _add_resources(self):

        if self.ie_html5_workaround and rendering_html5():
            self.metadata.resources.insert(
                0,
                Script(
                    "/cocktail/scripts/html5shiv-printshiv.js",
                    ie_condition = "lt IE 9"
                )
            )

        for resource in self.metadata.resources:
            if resource.mime_type == "text/javascript":
                self._add_core_scripts()
                break

        resource_sets = self.create_resource_sets()

        if resource_sets:
            remaining_resources = []

            for resource in self.metadata.resources:
                for resource_set in resource_sets:
                    if resource_set.matches(resource):
                        resource_set.append(resource)
                        break
                else:
                    remaining_resources.append(resource)

            for resource_set in resource_sets:
                resource_set.insert_into_document(self)
        else:
            remaining_resources = self.metadata.resources

        for resource in remaining_resources:
            resource.link(self)

    def create_resource_sets(self):
        resource_sets = []

        for resource_set_spec in self.resource_sets:
            if isinstance(resource_set_spec, tuple):
                resource_set = resource_set_spec[0](**resource_set_spec[1])
            elif callable(resource_set_spec):
                resource_set = resource_set_spec()
            else:
                raise TypeError(
                    "Bad resource set spec: %s. Expected a callable, or a "
                    "callable/kwargs tuple."
                    % resource_set_spec
                )
            resource_sets.append(resource_set)

        return resource_sets

    def _add_core_scripts(self):

        if not self.__core_scripts_added:
            self.__core_scripts_added = True

            for uri in reversed(self.core_scripts):
                self.metadata.resources.insert(0, uri)

            language = self.metadata.language or get_language()
            self.client_setup.append(
                "\t\tcocktail.setLanguage(%s);\n"
                % dumps(language)
            )

            init_code = "cocktail.init();"

            if self.root_element_id:
                init_code = (
                    "cocktail.rootElement =  document.getElementById(%s); "
                    % dumps(self.root_element_id)
                ) + init_code

            self.client_setup.append(
                "\t\tjQuery(function () { %s });\n" % init_code
            )

    def _add_client_variables(self):

        if self.metadata.client_variables:
            self._add_core_scripts()

            for key, value in self.metadata.client_variables.iteritems():
                self.client_setup_container.append(
                    "\t\tcocktail.setVariable(%s, %s);\n" % (
                        dumps(key), dumps(value)
                    )
                )

    def _add_client_translations(self):

        if self.metadata.client_translations:
            self._add_core_scripts()

            language = self.metadata.language or get_language()

            self.client_setup_container.append(
                "".join(
                    "\t\tcocktail.setTranslation(%s, %s);\n" % (
                        dumps(key),
                        dumps(translations[language][key])
                            if language in translations
                            and key in translations[language]
                            else ""
                    )
                    for key in self.metadata.client_translations
                )
            )

    def _add_client_models(self):

        if self.metadata.client_models:
            self._add_core_scripts()
            all_client_models = {}

            while self.metadata.client_models:
                client_models = self.metadata.client_models.items()
                self.metadata.client_models = {}

                for model_id, model_data in client_models:

                    all_client_models[model_id] = model_data
                    (cm_content, cm_metadata) = model_data

                    # Serialize the client model content as a javascript string
                    self.client_setup_container.append(
                        "\t\tcocktail._clientModel(%s).html = '%s';\n" % (
                            dumps(model_id),
                            cm_content
                                .replace("'", "\\'")
                                .replace("\n", "\\n")
                                .replace("&", "\\u0026")
                                .replace("<", "\\u003C")
                        )
                    )
                    self.metadata.update(cm_metadata)

            self.metadata.client_models = all_client_models

    def _add_content(self):
        self.body.append(self.content)

