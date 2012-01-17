#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
from cocktail.html.utils import escape_attrib

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

HTML5 = u"""<!DOCTYPE HTML>"""


class Renderer(object):

    doctype = None
    single_tags = "img", "link", "meta", "br", "hr", "input"
    flag_attributes = "selected", "checked", "autofocus"
    outputs_xml = False

    def write_element(self, element, rendering):

        tag = element.tag
        out = rendering.write

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
                        value = escape_attrib(unicode(value))
                        out(key + u'="' + value + u'"')

            # Single tag closure
            if tag in self.single_tags:

                if element.children:
                    raise RenderingError(
                        "Children not allowed on <%s> tags" % tag)

                out(self.single_tag_closure)
                return

            # Beginning of tag content
            else:
                out(u">")
        
        for child in element.children:
            rendering.render_element(child)

        if tag:
            out(u"</" + tag + u">")


class HTMLRenderer(Renderer):

    single_tag_closure = u">"
    html_version = None

    def _write_flag(self, key, out):
        out(key)


class HTML4Renderer(HTMLRenderer):
    doctype = HTML4_STRICT
    html_version = 4
    

class HTML5Renderer(HTMLRenderer):
    doctype = HTML5
    html_version = 5


class XHTMLRenderer(Renderer):

    doctype = XHTML1_STRICT
    single_tag_closure = u"/>"
    html_version = 4
    outputs_xml = True

    def _write_flag(self, key, out):
        out(key + u'="' + key + u'"')


class XHTML5Renderer(XHTMLRenderer):
    doctype = HTML5
    html_version = 5


html4_renderer = HTML4Renderer()
html5_renderer = HTML5Renderer()
xhtml_renderer = XHTMLRenderer()
xhtml5_renderer = XHTML5Renderer()

default_renderer = html4_renderer

class RenderingError(Exception):
    """An error raised when trying to render an incorrect element."""

