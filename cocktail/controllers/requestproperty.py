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
            properties = getattr(cherrypy.request, "_handler_properties", None)
            values = properties and properties.get(self)

            if values is None:
                value = _undefined
            else:
                value = values.get(instance, _undefined)

            if value is _undefined:
                value = self(instance)
                self.__set__(instance, value)

            return value

    def __set__(self, instance, value):
        
        properties = getattr(cherrypy.request, "_handler_properties", None)

        if properties is None:
            properties = WeakKeyDictionary()
            cherrypy.request._handler_properties = properties
        
        values = properties.get(self)

        if values is None:
            values = WeakKeyDictionary()
            properties[self] = values
        
        values[instance] = value

    def clear(self, instance):
        
        properties = getattr(cherrypy.request, "_handler_properties", None)

        if properties:
            values = properties.get(self)

            if values is not None:
                values.pop(instance, None)

