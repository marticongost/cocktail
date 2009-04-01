#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""

class DataBoundControl(object):

    binding_delegate = None

    def __init__(self):
        self.when_binding(self._bind_member)

    def _bind_member(self, control = None):

        if self.member and self.member.name:

            if self.data_display:
                name = self.data_display.get_member_name(
                    self.member,
                    self.language
                )
            else:
                name = self.member.name

                if self.language:
                    name += "-" + self.language

            (control or self.binding_delegate or self)["name"] = name

