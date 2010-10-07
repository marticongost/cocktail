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


def get_rendering_engine(engine_name, options = None):
 
    if rendering_options and options:
        custom_options = options
        options = rendering_options.copy()
        options.update(custom_options)
    elif options is None:
        options = rendering_options

    return buffet.available_engines[engine_name](options = options)

