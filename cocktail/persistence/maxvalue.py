#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from persistent import Persistent


class MaxValue(Persistent):

    value = None
    
    def __init__(self, value = None):
        self.value = value

    def _p_resolveConflict(self, old_state, saved_state, new_state):
        old_state["value"] = max(
            saved_state.get("value"),
            new_state.get("value")
        )        
        return old_state

