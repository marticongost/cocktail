#-*- coding: utf-8 -*-
u"""
Allows creating presentation components from XML markup.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
from cocktail.html.templates.loader import TemplateLoader

# Default template loader
_loader = None
get_class = None
new = None

def get_loader():
    return _loader

def set_loader(loader):
    global _loader, get_class, new
    _loader = loader
    get_class = loader.get_class
    new = loader.new

set_loader(TemplateLoader())

