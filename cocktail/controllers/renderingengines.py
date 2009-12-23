#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
import buffet
import cherrypy

_rendering_engines = {}

def get_rendering_engine(engine_name):

    engine = _rendering_engines.get(engine_name)

    if engine is None:
        engine_type = buffet.available_engines[engine_name]
        engine_options = \
            cherrypy.request.config.get("rendering.engine_options")
        engine = engine_type(options = engine_options)
        _rendering_engines[engine_name] = engine

    return engine

