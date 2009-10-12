#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""

def modal_selector(element):
    
    element.add_resource("/cocktail/scripts/modalselector.js")
    element.add_class("modal_selector")
    
    for key in ("accept button", "cancel button", "select button"):
        element.add_client_translation(
            "cocktail.html.modal_selector " + key
        )

