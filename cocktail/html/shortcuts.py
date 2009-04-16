#-*- coding: utf-8 -*-
u"""
Utilities to set shortcut keys on elements.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from cocktail.translations import translations

TRANSLATION_PREFIX = "cocktail.html.shortcuts "

def set_translated_shortcut(element, translation_key, target = None):
    key = translations(TRANSLATION_PREFIX + translation_key)
    if key:
        set_shortcut(element, key, target)

def set_shortcut(element, key, target = None):
    element.add_resource("/cocktail/scripts/shortcuts.js")
    
    if target is None:
        element.add_client_code("cocktail.setShortcut(this, '%s')" % key)
    else:
        element.add_client_code(
            "cocktail.setShortcut(this, '%s', jQuery('%s', this).get(0))"
            % (key, target)
        )

