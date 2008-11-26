#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
from simplejson import dumps
from cocktail.html.element import (
    Element, Content, _thread_data, IdGenerationError
)
from cocktail.html.resources import Script, StyleSheet
from cocktail.html.autoid import begin_id_generation, end_id_generation
from cocktail.translations import get_language, translations


class Page(Element):

    doctype = None
    content_type = "text/html"
    charset = "utf-8"
    styled_class = False
    tag = "html"
    __generated_id = None
    generated_id_format = "_element%d"

    CORE_SCRIPT = "/cocktail/scripts/core.js"
    JQUERY_SCRIPT = "/cocktail/scripts/jquery.js"

    HTTP_EQUIV_KEYS = frozenset((
        "content-type",
        "expires",
        "refresh",
        "set-cookie"
    ))

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self.__element_id = 0
        self.__title = None
        self.__meta = {}
        self.__resource_uris = set()        
        self.__resources = []
        self.__client_translations = set()
        self.__client_variables = {}
        self.__elements_with_client_params = []

    def _build(self):
      
        self.head = Element("head")
        self.append(self.head)

        self.body = Element("body")
        self.append(self.body)

        self._body_markup = Content()
        self.append(self._body_markup)

    def _render(self, renderer, out):
        
        _thread_data.rendered_page = self
        self.__generated_id = 0

        try:
            if self.doctype:
                out(self.doctype)
                out("\n")

            # Render the <body> element first, to gather meta information from all
            # elements (meta tags, scripts, style sheets, the page title, etc)
            renderer.before_element_rendered(self._before_descendant_rendered)
            renderer.after_element_rendered(self._after_descendant_rendered)
            self._body_markup.value = self.body.render(renderer)
            self._fill_head()
            
            # Then proceed with the full page. The <body> element is hidden so that
            # it won't be rendered a second time
            self.body.visible = False
            Element._render(self, renderer, out)
            self.body.visible = True

        finally:
            _thread_data.rendered_page = None
            self.__generated_id = None

    def _before_descendant_rendered(self, descendant):       

        if descendant.client_params:
            self.__elements_with_client_params.append(descendant)

    def _after_descendant_rendered(self, descendant):

        page_title = descendant.page_title
        
        # Page title
        if page_title is not None:
            self.__title = page_title

        # Meta tags
        self.__meta.update(descendant.meta)

        # Resources
        for resource in descendant.resources:
            uri = resource.uri
            if uri not in self.__resource_uris:
                self.__resource_uris.add(uri)
                self.__resources.append(resource)
        
        # Client variables and translations
        self.__client_variables.update(descendant.client_variables)
        self.__client_translations.update(descendant.client_translations)

    def _fill_head(self):

        head = self.head

        if self.content_type:
            ctype = self.content_type
            if self.charset:
                ctype += ";charset=" + self.charset

            self.__meta["content-type"] = ctype

        for key, value in self.__meta.iteritems():
            key_attrib = key in self.HTTP_EQUIV_KEYS and "http-equiv" or "name"
            meta_tag = Element("meta")
            meta_tag[key_attrib] = key
            meta_tag["content"] = value
            head.append(meta_tag)

        if self.__title and self.__title is not None:
            import re
            html_expr = re.compile(r"</?[^>]+>")
            title_tag = Element("title")
            title_tag.append(html_expr.sub("", self.__title))
            head.append(title_tag)
                        
        if self.__client_translations:
            self._add_resource_to_head(Script(self.CORE_SCRIPT), True)
                    
            language = get_language()
            
            script_tag = Element("script")
            script_tag["type"] = "text/javascript"
            script_tag.append("cocktail.setLanguage(%s);\n" % dumps(language))  
            script_tag.append("\n".join(
                "cocktail.setTranslation(%s, %s);"
                    % (dumps(key), dumps(translations[language][key]))
                for key in self.__client_translations
            ))
            head.append(script_tag)
        
        if self.__client_variables:
            script_tag = Element("script")
            script_tag["type"] = "text/javascript"
            script_tag.append("\n".join(
                "%s = %s;" % (key, dumps(value))
                for key, value in self.__client_variables.iteritems()
            ))
            head.append(script_tag)

        if self.__elements_with_client_params:
            
            self._add_resource_to_head(Script(self.JQUERY_SCRIPT), True)
            
            script_tag = Element("script")
            script_tag["type"] = "text/javascript"            
            js = ["jQuery(function () {"]
            
            for element in self.__elements_with_client_params:
                js.append("\tjQuery('#%s').each(function () {\n" % element["id"])
                
                for key, value in element.client_params.iteritems():
                    js.append("\t\tthis.%s = %s;" % (key, dumps(value)))
                
                js.append("\t});")
            
            js.append("});")
            script_tag.append("\n".join(js))
            head.append(script_tag)
        
        for resource in self.__resources:
            self._add_resource_to_head(resource)
         
    def _add_resource_to_head(self, resource, always = False):
        
        uri = resource.uri
        
        if always or uri in self.__resource_uris:
            
            self.__resource_uris.discard(uri)
        
            if isinstance(resource, Script):
                script_tag = Element("script")
                script_tag["type"] = resource.mime_type
                script_tag["src"] = uri
                self.head.append(script_tag)
    
            elif isinstance(resource, StyleSheet):
                link_tag = Element("link")
                link_tag["rel"] = "Stylesheet"
                link_tag["type"] = resource.mime_type
                link_tag["href"] = uri
                self.head.append(link_tag)
       
    def generate_element_id(self):

        if self.__generated_id is None:
            raise IdGenerationError()

        id = self.generated_id_format % self.__generated_id
        self.__generated_id += 1
        return id

