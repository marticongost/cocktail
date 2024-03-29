#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.persistence.zodbdebugger import ZODBDebugger


def zodb_debugger():

    cmd = cherrypy.request.params.get("zodb_debug")

    if cmd:
        cmd_parts = cmd.split("-", 1)
        action = cmd_parts[0]

        if action in ("count", "blame", "interrupt"):

            handler = cherrypy.request.handler

            def instrumented_handler(*args, **kwargs):
                with ZODBDebugger(
                    filter = cmd_parts[1] if len(cmd_parts) > 1 else None,
                    action = action
                ):
                    return handler(*args, **kwargs)

            cherrypy.request.handler = instrumented_handler

cherrypy.tools.zodb_debugger = cherrypy.Tool(
    'before_handler',
    zodb_debugger
)

