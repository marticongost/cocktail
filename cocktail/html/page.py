#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
from simplejson import dumps
from cocktail.html.element import (
    Element, Content, _thread_data, IdGenerationError
)
from cocktail.html.resources import Resource, Script, StyleSheet
from cocktail.translations import get_language, translations


class Page(Element):

    doctype = None
    content_type = "text/html"
    charset = "utf-8"
    styled_class = False
    tag = "html"

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
        self.__client_translations = set()
        self.__client_variables = {}
        self.__client_params_script = None
        self.__client_model_stack = []

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

    def _before_descendant_rendered(self, descendant, renderer):

        if descendant.client_model:
            self.__client_model_stack.append(descendant.client_model)

        for element in descendant.head_elements:
            self.head.append(Content(element.render(renderer)))

        client_params = descendant.client_params
        client_code = descendant.client_code

        if client_params or client_code:
            
            self._add_resource_to_head(self.JQUERY_SCRIPT)
            self._add_resource_to_head(self.CORE_SCRIPT)
             
            if self.__client_params_script is None:
                
                script_tag = Element("script")
                script_tag["type"] = "text/javascript"
                script_tag.append("jQuery(function () {\n")
                
                self.__client_params_script = Content()
                self.__client_params_script.value = ""
                script_tag.append(self.__client_params_script)
                script_tag.append("});\n")
                self.head.append(script_tag)

            client_model = (
                self.__client_model_stack
                and self.__client_model_stack[-1]
            )

            js = []

            if client_model:
                
                client_model_ref = "\tcocktail._clientModel('%s'" \
                    % client_model

                if not descendant.client_model:
                    client_model_ref += ", '%s'" % descendant["id"]

                client_model_ref += ")"

                if client_params:
                    js.append(client_model_ref + ".params = %s;\n"
                        % dumps(descendant.client_params)
                    )

                if client_code:
                    js.append(client_model_ref + ".code = %s;\n"
                        % dumps(list(descendant.client_code))
                    )
            else:
                js.append(
                    "\tjQuery('#%s').each(function () {" % descendant["id"]
                )
                
                for key, value in client_params.iteritems():
                    js.append("\t\tthis.%s = %s;" % (key, dumps(value)))
                
                js.extend("\t\t" + snippet for snippet in client_code)
                js.append("\t});\n")
            
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
            self._add_resource_to_head(resource)
        
        # Client variables and translations
        self.__client_variables.update(descendant.client_variables)
        self.__client_translations.update(descendant.client_translations)

        if descendant.client_model:
            self.__client_model_stack.pop(-1)

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
            self._add_resource_to_head(self.CORE_SCRIPT)
            
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
        
        if self.CORE_SCRIPT in self.__resource_uris:
            script_tag = Element("script")
            script_tag["type"] = "text/javascript"
            script_tag.append("jQuery(function () { cocktail.init(); });")
            self.head.append(script_tag)

    def _add_resource_to_head(self, resource):
        
        is_string = isinstance(resource, basestring)

        uri = resource if is_string else resource.uri
        
        if uri not in self.__resource_uris:
            self.__resource_uris.add(uri)
            
            if is_string:
                resource = Resource.from_uri(uri)

            if isinstance(resource, Script):
                
                if uri == self.CORE_SCRIPT:
                    self._add_resource_to_head(self.JQUERY_SCRIPT)
                elif uri != self.JQUERY_SCRIPT:
                    self._add_resource_to_head(self.CORE_SCRIPT)

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
      

