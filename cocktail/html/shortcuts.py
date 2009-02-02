#-*- coding: utf-8 -*-
"""
Utilities to set shortcut keys on elements.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from cocktail.translations import translate

TRANSLATION_PREFIX = "cocktail.html.shortcuts "

def set_translated_shortcut(element, translation_key):
    key = translate(TRANSLATION_PREFIX + translation_key, default = "")
    if key:
        set_shortcut(element, key)

def set_shortcut(element, key):
    element.add_resource("/cocktail/scripts/shortcuts.js")
    element.add_client_code("cocktail.setShortcut(this, '%s')" % key)

