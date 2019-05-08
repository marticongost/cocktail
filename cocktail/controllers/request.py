#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.urls import URLBuilder, QueryString

_default_ports = {"http": 80, "https": 443}

def get_request_root_url():
    try:
        return cherrypy.request._cocktail_request_root_url
    except AttributeError:
        url = get_request_root_url_builder().get_url()
        cherrypy.request._cocktail_request_root_url = url
        return url

def get_request_url():
    try:
        return cherrypy.request._cocktail_request_url
    except AttributeError:
        url = get_request_url_builder().get_url()
        cherrypy.request._cocktail_request_url = url
        return url

def get_request_query(**kwargs):
    url = get_request_url()
    if kwargs:
        return url.query.merge(**kwargs)
    else:
        return url.query

def get_request_root_url_builder():

    url_builder = URLBuilder()
    headers = cherrypy.request.headers
    base = cherrypy.request.base

    if base:
        scheme, rest = base.split("://")
        url_builder.scheme = headers.get('X-Forwarded-Scheme') or scheme
        pos = rest.find(":")
        if pos == -1:
            url_builder.hostname = rest
        else:
            url_builder.hostname = rest[:pos]
            url_builder.port = rest[pos+1:]

    elif cherrypy.server.socket_host:
        url_builder.scheme = headers.get('X-Forwarded-Scheme', 'http')
        url_builder.hostname = cherrypy.server.socket_host
        port = cherrypy.server.socket_port
        if port:
            if port != _default_ports.get(url_builder.scheme):
                url_builder.port = port

    return url_builder

def get_request_url_builder():
    req = cherrypy.request
    url_builder = get_request_root_url_builder()
    url_builder.path = req.script_name + req.path_info
    url_builder.query = req.query_string
    return url_builder

