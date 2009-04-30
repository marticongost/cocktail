#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from inspect import getmro

_undefined = object()

class TypeMapping(dict):

    def __getitem__(self, cls):
        
        value = self.get(cls, _undefined)

        if value is _undefined:
            raise KeyError(cls)
        
        return value

    def get(self, cls, default = None):
        for cls in getmro(cls):
            value = dict.get(self, cls, _undefined)
            if value is not _undefined:
                return value
        else:
            return default


