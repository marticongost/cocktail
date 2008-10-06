#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""

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
       
class Renderer(object):
    
    doctype = None
    single_tags = "img", "link", "meta", "br", "hr"
    flag_attributes = "selected", "checked"

    def make_page(self, element):        
        from cocktail.html.page import Page
        page = Page()
        page.doctype = self.doctype
        page.body.append(element)
        return page

    def write_element(self, element, out):
        
        tag = element.tag
        render_children = True

        if tag:
            # Tag opening
            out(u"<")
            out(tag)

            # Attributes
            for key, value in element.attributes.iteritems():
                if value != False and value is not None:
                    self._write_attribute(key, value, out)

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

            if tag:
                out(u"</")
                out(tag)
                out(u">")

    def _write_attribute(self, key, value, out):
        
        out(u" ")

        if key in self.flag_attributes:
            if value:
                self._write_flag(key, out)
        else:
            out(key)
            out(u"=")
            out(self._serialize_attribute_value(value))

    def _serialize_attribute_value(self, value):
        return u'"' + unicode(value).replace(u'"', u'\\"') + u'"'

class HTML4Renderer(Renderer):

    doctype = HTML4_STRICT
    single_tag_closure = u">"

    def _write_flag(self, key, out):
        out(key)

class XHTMLRenderer(Renderer):
    
    doctype = XHTML1_STRICT
    single_tag_closure = u"/>"

    def _write_flag(self, key, out):
        out(key)
        out(u'="')
        out(key)
        out(u'"')

DEFAULT_RENDERER_TYPE = HTML4Renderer

class RenderingError(Exception):
    pass

