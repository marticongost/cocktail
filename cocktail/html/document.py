#-*- coding: utf-8 -*-
u"""Defines the `HTMLDocument` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from simplejson import dumps
from cocktail.translations import translations, get_language
from cocktail.html.element import Element, Content
from cocktail.html.ieconditionalcomment import IEConditionalComment
from cocktail.html.resources import Script, StyleSheet
from cocktail.html.rendering import Rendering
from cocktail.html.utils import rendering_html5, rendering_xml
from cocktail.html.documentmetadata import DocumentMetadata

HTTP_EQUIV_KEYS = frozenset((
    "content-type",
    "expires",
    "refresh",
    "set-cookie"
    "X-UA-Compatible"
))


class HTMLDocument(Element):
    """An object that creates the document structures used when rendering an
    element as a full page.
    """
    __core_scripts_added = False
    core_scripts = [
        "/cocktail/scripts/jquery.js",
        "/cocktail/scripts/core.js"
    ]

    tag = "html"
    styled_class = False
    content = ""
    metadata = DocumentMetadata()
    rendering_options = {}
    ie_html5_workaround = True

    def _render(self, rendering):

        doctype = self.metadata.doctype or rendering.renderer.doctype
        
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
        self.client_setup.append("// cocktail.html client-side setup\n")
        self.head.append(self.client_setup)
        
        self.client_setup_container = Element(None)
        self.client_setup.append(self.client_setup_container)

        self.body = Element("body")
        self.append(self.body)

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
        self._add_client_params()
        self._add_client_variables()
        self._add_client_code()
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
        ct_meta = Element("meta")
        ct_meta["http-equiv"] = "Content-Type"
        ct_meta["content"] = "%s;%s" % (
            self.metadata.content_type or "text/html",
            self.metadata.charset or "utf-8"
        )
        self.meta_container.append(ct_meta)

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
            self.scripts_container.append(
                IEConditionalComment("lt IE 9", children = [
                    Element("script", children = [
                        """
                        (function(){    
                            var html5Tags = "address|article|aside|audio|canvas|command|datalist|details|dialog|figure|figcaption|footer|header|hgroup|keygen|mark|meter|menu|nav|progress|ruby|section|time|video".split('|');
                            for (var i = 0; i < html5Tags.length; i++){
                                document.createElement(html5Tags[i]);
                            }
                        })();                        
                        """
                    ])
                ])
            )

        for resource in self.metadata.resources:
            self._add_resource(resource)

    def _add_resource(self, resource):

        if isinstance(resource, Script):
            self._add_core_scripts()
            script = Element("script")
            script["type"] = resource.mime_type
            script["src"] = resource.uri
            script = self._apply_ie_condition(resource, script)
            self.scripts_container.append(script)

        elif isinstance(resource, StyleSheet):
            style_sheet = Element("link")
            style_sheet["rel"] = "Stylesheet"
            style_sheet["type"] = resource.mime_type
            style_sheet["href"] = resource.uri
            style_sheet = self._apply_ie_condition(resource, style_sheet)
            self.styles_container.append(style_sheet)

        else:
            raise TypeError(
                "%s is not capable of rendering %s, unknown resource type."
                % (self, resource)
            )

    def _apply_ie_condition(self, resource, element):
        if resource.ie_condition:
            comment = IEConditionalComment(resource.ie_condition)
            comment.append(element)
            return comment
        else:
            return element

    def _add_core_scripts(self):
        
        if not self.__core_scripts_added:
            self.__core_scripts_added = True
            
            for uri in self.core_scripts:
                script = Script(uri)
                if script not in self.metadata.resources:
                    self._add_resource(script)

            language = self.metadata.language or get_language()
            self.client_setup.append(
                "\t\tcocktail.setLanguage(%s);\n"
                % dumps(language)
            )

            self.client_setup.append(
                "\t\tjQuery(function () { cocktail.init(); });\n"
            )

    def _add_client_params(self):

        if self.metadata.client_params:
            self._add_core_scripts()

            for id, values in self.metadata.client_params.iteritems():
                js = "\t\tcocktail.__clientParams['%s'] = %s;\n" % (
                    id,
                    dumps(values)
                )
                self.client_setup_container.append(js)

    def _add_client_code(self):

        if self.metadata.client_code:
            self._add_core_scripts()
            
            for id,code_snippets in self.metadata.client_code.iteritems():
                js = "\t\tcocktail.__clientCode['%s'] = [%s];\n" % (
                    id,
                    ", ".join(
                        "function () { %s }" % snippet
                        for snippet in code_snippets
                    )
                )
                self.client_setup_container.append(js)

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

                for model_id, element in client_models:
                    
                    all_client_models[model_id] = element

                    cm_rendering = Rendering(
                        rendered_client_model = element,
                        **self.rendering_options
                    )
                    cm_metadata = cm_rendering.document_metadata
                    cm_rendering.render_element(element)

                    # Serialize the client model content as a javascript string
                    cm_str = "'" + element.client_model + "'"
                    self.client_setup_container.append(
                        "\t\tcocktail._clientModel(%s).html = '%s';\n" % (
                            cm_str,
                            cm_rendering
                                .markup()
                                .replace("'", "\\'")
                                .replace("\n", "\\n")
                                .replace("&", "\\x26")
                                .replace("<", "\\x3C")
                        )
                    )

                    # Declare client side parameters and initialization code for
                    # the client model and its nested content. This special
                    # treatment is necessary to allow client models to apply this
                    # initialization each time they are instantiated.
                    cm_id = element["id"]
                    for id, values in cm_metadata.client_params.iteritems():
                        self.client_setup_container.append(
                            "\t\tcocktail._clientModel(%s).params = %s;\n" % (
                                cm_str 
                                    if id == cm_id
                                    else cm_str + ", '%s'" % id,
                                dumps(values)
                            )
                        )

                    for id, snippets in cm_metadata.client_code.iteritems():
                        self.client_setup_container.append(
                            "\t\tcocktail._clientModel(%s).code = %s;\n" % (
                                cm_str
                                    if id == cm_id
                                    else cm_str + ", '%s'" % id,
                                dumps(snippets)
                            )
                        )

                    # Apply any remaining metadata supplied by the client model or
                    # its content to the document.
                    cm_metadata.client_params = {}
                    cm_metadata.client_code = {}            
                    self.metadata.update(cm_metadata)

            self.metadata.client_models = all_client_models

    def _add_content(self):
        self.body.append(self.content)

