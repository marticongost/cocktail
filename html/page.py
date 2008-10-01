#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
from cocktail.html.element import Element
from cocktail.html.resources import Script, StyleSheet

class Page(Element):

    doctype = None
    content_type = "text/html"
    charset = "utf-8"
    styled_class = False
    tag = "html"

    HTTP_EQUIV_KEYS = frozenset((
        "content-type",
        "expires",
        "refresh",
        "set-cookie"
    ))

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self.__title = None
        self.__meta = {}
        self.__resource_uris = set()
        self.__resources = []

    def _build(self):
      
        self.head = Element("head")
        self.append(self.head)

        self.body = Element("body")
        self.append(self.body)

    def _render(self, renderer, out):
        
        if self.doctype:
            out(self.doctype)
            out("\n")

        Element._render(self, renderer, out)

    def _descendant_ready(self, descendant):

        page_title = descendant.page_title
        
        if page_title is not None:
            self.__title = page_title

        self.__meta.update(descendant.meta)

        for resource in descendant.resources:
            uri = resource.uri
            if uri not in self.__resource_uris:
                self.__resource_uris.add(uri)
                self.__resources.append(resource)

    def _content_ready(self):

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
            title_tag = Element("title")
            title_tag.append(self.__title)
            head.append(title_tag)
        
        for resource in self.__resources:
            
            if isinstance(resource, Script):
                script_tag = Element("script")
                script_tag["type"] = resource.mime_type
                script_tag["src"] = resource.uri
                head.append(script_tag)

            elif isinstance(resource, StyleSheet):
                link_tag = Element("link")
                link_tag["rel"] = "Stylesheet"
                link_tag["type"] = resource.mime_type
                link_tag["href"] = resource.uri
                head.append(link_tag)

