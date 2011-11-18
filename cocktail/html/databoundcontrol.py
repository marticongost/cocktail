#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from warnings import warn

class DataBoundControl(object):

    binding_delegate = None

    def __init__(self):
        warn(
            "The DataBoundControl class has been deprecated in favor of the "
            "data_bound() function",
            DeprecationWarning,
            stacklevel = 2
        )

        data_bound(self)

    def _bind_member(self, control = None):
        bind_member(self, control)


def data_bound(element, control = None):
    @element.when_binding
    def binding():
        bind_member(element, control)
    
def bind_member(element, control = None):

    member = getattr(element, "collection", None) or element.member

    if member and member.name:

        if element.data_display:
            name = element.data_display.get_member_name(
                member,
                element.language
            )
        else:
            name = member.name
            if element.language:
                name += "-" + element.language

        control = control or getattr(element, "binding_delegate", element)

        if hasattr(control, "name"):
            control.name = name
        else:
            control["name"] = name

