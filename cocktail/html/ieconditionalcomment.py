#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import Element, Content


class IEConditionalComment(Element):

    tag = None
    condition = None
	
    def __init__(self, condition = None, **kwargs):		
        Element.__init__(self, **kwargs)
        self.condition = condition
	
    def _render(self, rendering):

        if self.rendered:
            condition = self.condition
            
            if condition:
                rendering.write(u"<!--[if %s]>" % condition)
            
            rendering.renderer.write_element(self, rendering)

            if condition:
                rendering.write(u"<![endif]-->")


class IEWrapper(Element):

    styled_class = False
    ie_versions = [6, 7, 8, 9]

    def _render(self, rendering):
        if self.rendered:

            if not self.ie_versions:
                Element._render(self, rendering)
                return

            css_class = self["class"] or ""

            for version in self.ie_versions:
                rendering.write(u"<!--[if IE %d]>" % version)
                self["class"] = (css_class + " IE IE%d" % version).lstrip()
                rendering.renderer.write_element_opening(self, rendering)
                rendering.write(u"<![endif]-->")

            rendering.write(u"<!--[if !IE]> -->")
            self["class"] = (css_class + " not_IE").lstrip()
            should_write_content = \
                rendering.renderer.write_element_opening(self, rendering)
            rendering.write(u"<!-- <![endif]-->")

            self["class"] = css_class

            if should_write_content:
                rendering.renderer.write_element_content(self, rendering)
                rendering.renderer.write_element_closure(self, rendering)

