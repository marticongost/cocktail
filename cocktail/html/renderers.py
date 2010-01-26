#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
import re

XHTML1_STRICT = u"""<!DOCTYPE html
PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">"""

XHTML1_TRANSITIONAL = u"""<!DOCTYPE html
PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">"""

HTML4_STRICT = u"""<!DOCTYPE html
PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">"""

HTML4_TRANSITIONAL = u"""<!DOCTYPE html
PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">"""

_entity_expr = re.compile("[\"<>&]")
_entity_dict = {
    "\"": "&quot;",
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;"
}
_entity_translation = lambda match: _entity_dict[match.group(0)]


class Renderer(object):

    doctype = None
    single_tags = "img", "link", "meta", "br", "hr", "input"
    flag_attributes = "selected", "checked"

    def __init__(self):
        self.__before_rendering = []
        self.__after_rendering = []

    def make_page(self, element):
        
        from cocktail.html.page import Page

        page = Page()
        page.doctype = self.doctype
        page.body.append(element)

        if element.page_content_type:
            page.content_type = element.page_content_type

        if element.page_charset:
            page.charset = element.page_charset

        return page

    def before_element_rendered(self, handler):
        self.__before_rendering.append(handler)

    def after_element_rendered(self, handler):
        self.__after_rendering.append(handler)

    def write_element(self, element, out):

        for handler in self.__before_rendering:
            handler(element, self)

        if element.client_model:
            out("<script type='text/javascript'>")
            out("cocktail._clientModel('%s').html = '" % element.client_model)
            wrapped_out = out
            def out(snippet):
                wrapped_out(snippet.replace("'", "\\'").replace("\n", "\\n"))

        tag = element.tag
        render_children = True

        if tag:
            # Tag opening
            out(u"<" + tag)

            # Attributes
            for key, value in element.attributes.iteritems():
                if value is not None \
                and not (isinstance(value, bool) and not value):

                    out(u" ")

                    if key in self.flag_attributes:
                        if value:
                            self._write_flag(key, out)
                    else:
                        value = _entity_expr.sub(
                            _entity_translation,
                            unicode(value)
                        )
                        out(key + u'="' + value + u'"')

            # Single tag closure
            if tag in self.single_tags:

                if element.children:
                    raise RenderingError(
                        "Children not allowed on <%s> tags" % tag)

                out(self.single_tag_closure)
                render_children = False

            # Beginning of tag content
            else:
                out(u">")

        if render_children:

            for child in element.children:
                child._render(self, out)

            element._content_ready()

            if tag:
                out(u"</" + tag + u">")

        if element.client_model:
            wrapped_out("';</script>")

        for handler in self.__after_rendering:
            handler(element, self)


class HTML4Renderer(Renderer):

    doctype = HTML4_STRICT
    single_tag_closure = u">"

    def _write_flag(self, key, out):
        out(key)


class XHTMLRenderer(Renderer):

    doctype = XHTML1_STRICT
    single_tag_closure = u"/>"

    def _write_flag(self, key, out):
        out(key + u'="' + key + u'"')


DEFAULT_RENDERER_TYPE = HTML4Renderer

class RenderingError(Exception):
    pass

