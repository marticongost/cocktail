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
	
    def _render(self, renderer, out):
        self.ready()
        if self.rendered:
            if self.condition:
                out(u"<!--[if %s]>" % self.condition)
            renderer.write_element(self, out)
            if self.condition:
                out(u"<![endif]-->")
