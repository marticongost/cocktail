#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from pkg_resources import iter_entry_points
rendering_options = {}
_engine_instances = []


def get_rendering_engine(engine_name, options = None):

    if rendering_options and options:
        custom_options = options
        options = rendering_options.copy()
        options.update(custom_options)
    elif options is None:
        options = rendering_options

    for engine_request, engine in _engine_instances:
        if engine_request == (engine_name, options):
            return engine

    for entry_point in iter_entry_points(
        "python.templating.engines",
        engine_name
    ):
        engine_class = entry_point.resolve()
        engine = engine_class(options = options.copy())
        _engine_instances.append(((engine_name, options), engine))
        return engine

    raise ValueError("Can't find an engine with name %r" % engine_name)

