#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.persistence.zodbdebugger import ZODBDebugger


def zodb_debugger():

    cmd = cherrypy.request.params.get("zodb_debug")

    if cmd:
        cmd_parts = cmd.split("-", 1)
        action = cmd_parts[0]

        if action in ("count", "interrupt"):
            with ZODBDebugger(
                filter = cmd_parts[1] if len(cmd_parts) > 1 else None,
                action = action
            ):
                return cherrypy.request.handler()

    # Debugger disabled
    return cherrypy.request.handler()

cherrypy.tools.zodb_debugger = cherrypy.Tool(
    'before_handler',
    zodb_debugger
)

