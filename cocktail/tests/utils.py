#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from copy import copy

class EventLog(list):

    def listen(self, *args, **kwargs):
        for slot in args:
            self._add_listener(slot)

        for name, slot in kwargs.iteritems():
            self._add_listener(slot, name)

    def _add_listener(self, slot, name = None):

        def listener(event):
            self.append(copy(event))

        if name:
            listener.func_name = name

        slot.append(listener)

    def clear(self):
        while self:
            self.pop(0)

