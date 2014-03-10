#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import templates

TextBox = templates.get_class("cocktail.html.TextBox")


class PasswordBox(TextBox):
    
    def __init__(self, *args, **kwargs):
        TextBox.__init__(self, *args, **kwargs)
        self["type"] = "password"

