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
from cocktail.translations import get_language, translations


class Page(Element):

    doctype = None
    content_type = "text/html"
    charset = "utf-8"
    styled_class = False
    tag = "html"
    __generated_id = None
    generated_id_format = "cocktail-element%d"

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
        self.__client_params_script = None

    def _build(self):
      
        self.head = Element("head")
        self.append(self.head)

        self._generated_head = Element()
        self._generated_head.tag = None
        self.head.append(self._generated_head)

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

    def _before_descendant_rendered(self, descendant, renderer):

        for element in descendant.head_elements:
            self.head.append(Content(element.render(renderer)))

        if descendant.client_params:
            
            if self.JQUERY_SCRIPT not in self.__resource_uris:
                self.__resource_uris.add(self.JQUERY_SCRIPT)
                self.__resources.append(Script(self.JQUERY_SCRIPT))
 
            if self.__client_params_script is None:
                                
                script_tag = Element("script")
                script_tag["type"] = "text/javascript"
                script_tag.append("jQuery(function () {\n")
                
                self.__client_params_script = Content()
                self.__client_params_script.value = ""
                script_tag.append(self.__client_params_script)
                
                script_tag.append("});\n")
                self.head.append(script_tag)
            
            js = ["\tjQuery('#%s').each(function () {" % descendant["id"]]
                
            for key, value in descendant.client_params.iteritems():
                js.append("\t\tthis.%s = %s;" % (key, dumps(value)))
                
            js.append("\t});")
            
            self.__client_params_script.value += "\n".join(js)

    def _after_descendant_rendered(self, descendant, renderer):

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

        head = self._generated_head

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
                self._generated_head.append(script_tag)
    
            elif isinstance(resource, StyleSheet):
                link_tag = Element("link")
                link_tag["rel"] = "Stylesheet"
                link_tag["type"] = resource.mime_type
                link_tag["href"] = uri
                self._generated_head.append(link_tag)
       
    def generate_element_id(self):

        if self.__generated_id is None:
            raise IdGenerationError()

        id = self.generated_id_format % self.__generated_id
        self.__generated_id += 1
        return id

