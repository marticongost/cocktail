#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.html.element import Element
from cocktail.html.uigeneration import default_display
from cocktail.html.hiddeninput import HiddenInput

def read_only_display(ui_generator, obj, member, value, **context):

    read_only_ui_generator = (
        ui_generator.read_only_ui_generator
        or default_display
    )

    element = Element()
    element.add_class("read_only_display")

    element.display = read_only_ui_generator.create_member_display(
        obj,
        member,
        value,
        **context
    )
    element.append(element.display)

    element.hidden_input = HiddenInput()
    element.append(element.hidden_input)
    element.data_binding_delegate = element.hidden_input
    return element

