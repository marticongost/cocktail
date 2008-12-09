#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from weakref import WeakKeyDictionary
import cherrypy

_undefined = object()


class request_property(property):
    
    def __init__(self, calculate, key = None, doc = None):
        self.__calculate = calculate,
        self.__doc__ = doc or calculate.__doc__
    
    def __call__(self, instance):
        return self.__calculate[0](instance)

    def __get__(self, instance, type = None):
        
        if instance is None:
            return self
        else:
            values = getattr(cherrypy.request, "_rp_values", None)

            if values is None:
                value = _undefined
            else:
                value = values.get((self, instance), _undefined)

            if value is _undefined:
                self.__set__(instance, self(instance))

            return value

    def __set__(self, instance, value):
        values = getattr(cherrypy.request, "_rp_values", None)

        if values is None:
            values = WeakKeyDictionary()
            cherrypy.request._rp_values = values
        
        values[(self, instance)] = value

    def clear(self, instance):
        values = getattr(cherrypy.request, "_rp_values", None)
        if values is not None:
            values.pop((self, instance), None)

