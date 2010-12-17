#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
import buffet
import cherrypy

rendering_options = {}
_engine_cache = []


def get_rendering_engine(engine_name, options = None):
 
    if rendering_options and options:
        custom_options = options
        options = rendering_options.copy()
        options.update(custom_options)
    elif options is None:
        options = rendering_options

    for engine_request, engine in _engine_cache:
        if engine_request[0] == engine_name and engine_request[1] == options:
            return engine

    engine = buffet.available_engines[engine_name](options = options.copy())
    _engine_cache.append(((engine_name, options), engine))
    return engine

