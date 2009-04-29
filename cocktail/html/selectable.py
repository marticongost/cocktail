#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
"""
from cocktail.html.datadisplay import (
    NO_SELECTION,
    SINGLE_SELECTION,
    MULTIPLE_SELECTION
)

def selectable(
    element,
    mode = SINGLE_SELECTION,
    entry_selector = None,
    checkbox_selector = None):
    
    element.add_resource(
        "/cocktail/scripts/jquery.disable.text.select.pack.js")
    element.add_resource("/cocktail/scripts/selectable.js")
    
    element.set_client_variable(
        "cocktail.NO_SELECTION", NO_SELECTION)
    element.set_client_variable(
        "cocktail.SINGLE_SELECTION", SINGLE_SELECTION)
    element.set_client_variable(
        "cocktail.MULTIPLE_SELECTION", MULTIPLE_SELECTION)

    element.add_class("selectable")
    element.set_client_param("selectableParams", {
        "mode": mode,
        "entrySelector": entry_selector,
        "checkboxSelector": checkbox_selector
    })

