#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy

def create_request_properties_container():
    cherrypy.request._cocktail_request_properties = {}

cherrypy.request.hooks.attach("on_start_resource", create_request_properties_container)

def clear_request_properties():
    properties = getattr(
        cherrypy, 
        "request._cocktail_request_properties",
        None
    )

    if properties:
        properties.clear()


class RequestProperty(object):
    """A decorator that allows controllers to define properties with a
    lifecycle bound to HTTP requests."""

    def __init__(self, getter = None):
        self._getter = getter or (lambda self: None)
        self.__doc__ = getter and getter.__doc__

    def __get__(self, instance, type = None):
        if instance is None:
            return self
        else:
            properties = cherrypy.request._cocktail_request_properties
            key = (self, instance)
            try:
                return properties[key]
            except KeyError:
                value = self._getter(instance)
                properties[key] = value
                return value

    def __set__(self, instance, value):
        properties = cherrypy.request._cocktail_request_properties
        properties[(self, instance)] = value

    def __call__(self, instance):
        return self._getter(instance)

    def __repr__(self):
        return "RequestProperty(%s)" % self.__call__

    def clear(self, instance):
        properties = cherrypy.request._cocktail_request_properties
        properties.pop((self, instance), None)


request_property = RequestProperty

