#-*- coding: utf-8 -*-
"""
Profiler tool for CherryPy request handlers.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from cProfile import runctx
from pstats import Stats
from threading import Lock
from pickle import dumps
from subprocess import Popen
import re
import os
from os.path import join
import shlex
from collections import Sequence
import cherrypy
from cocktail.controllers.request import get_request_url
from cocktail.controllers.static import serve_file

_lock = Lock()
_request_id = 0
default_viewer = None

try:
    from pyprof2calltree import convert
except ImportError:
    convert = None
    default_viewer = None
else:
    if os.path.exists("/usr/bin/kcachegrind"):
        default_viewer = "/usr/bin/dbus-launch " \
                         "/usr/bin/kcachegrind %(calltree)s"

def handler_profiler(
    stats_path = "/tmp",
    default_action = None,
    trigger = None,
    viewer = None,
    filter = None
):
    if trigger:
        trigger_action = cherrypy.request.params.get(trigger)
        profiler_action = trigger_action or default_action
    else:
        profiler_action = default_action
        trigger_action = None

    if not profiler_action:
        return

    if filter and not trigger_action:

        if not isinstance(filter, Sequence):
            filter = (filter,)

        for expr in filter:

            if isinstance(expr, str):
                url = get_request_url()
                if expr.startswith("!"):
                    reg_expr = re.compile(expr[1:])
                    match = not reg_expr.search(url)
                else:
                    reg_expr = re.compile(expr)
                    match = reg_expr.search(url)
            elif callable(expr):
                match = expr()
            else:
                raise ValueError(
                    "Profiler filter expressions should be a string or a "
                    "callable, not %r" % expr
                )

            if not match:
                return

    handler = cherrypy.request.handler

    if viewer is None:
        viewer = default_viewer

    def profiled_handler(*args, **kwargs):

        global _request_id

        # Acquire a unique identifier for the request
        with _lock:
            _request_id += 1
            id = _request_id

        name = cherrypy.request.path_info.strip("/").replace("/", "-")
        name += "." + str(id)

        # Create the execution context for the profiler
        local_context = {
            "handler": handler,
            "args": args,
            "kwargs": kwargs,
            "rvalue": None
        }

        # Run the handler for the current request through the profiler.
        # Profile data is either shown on standard output or stored on the
        # indicated file.
        stats_file = join(stats_path, "%s.stats" % name) if stats_path else None

        try:
            runctx(
                "rvalue = handler(*args, **kwargs)",
                globals(),
                local_context,
                stats_file
            )
        finally:

            # If pyprof2calltree is available, use it to export the profiler stats
            # from Python's own format to 'calltree' (which can be parsed by
            # kcachegrind and others)
            calltree_file = None

            if stats_file is not None and convert is not None:
                calltree_file = join(stats_path, "%s.calltree" % name)
                convert(stats_file, calltree_file)

            if profiler_action == "view":

                if not viewer:
                    raise ValueError(
                        "No value defined for the "
                        "tools.handler_profiler.viewer setting; can't use the "
                        "'view' profiler action"
                    )

                cmd = shlex.split(viewer % {
                    "stats": stats_file,
                    "calltree": calltree_file
                })
                env = os.environ.copy()
                env.setdefault("DISPLAY", ":0")
                proc = Popen(cmd, env = env)

            if profiler_action == "download":
                return serve_file(
                    calltree_file or stats_file,
                    "application/octet-stream",
                    "attachment"
                )

        return local_context["rvalue"]

    cherrypy.request.handler = profiled_handler

cherrypy.tools.handler_profiler = cherrypy.Tool(
    'before_handler',
    handler_profiler
)

if __name__ == "__main__":

    import sys
    from optparse import OptionParser
    from pprint import pprint
    from pickle import loads

    parser = OptionParser()
    parser.add_option("-s", "--sort",
        help = "The sorting order for the profile data. "
        "Accepts the same values as the pstats.Stats.sort_stats() "
        "method."
    )
    parser.add_option("-t", "--top",
        type = "int",
        help = "Limits data to the first N rows."
    )
    parser.add_option("-p", "--path",
        default = ".",
        help = "The folder where the profiling information resides."
    )

    options, args = parser.parse_args()

    if not args:
        sys.stderr.write("Need one or more profile identifiers\n")
        sys.exit(1)

    for arg in args:

        # Load context
        context_path = join(options.path, "%s.context" % arg)
        context_file = open(context_path, "r")
        try:
            context = loads(context_file.read())
        finally:
            context_file.close()

        # Load stats
        stats_path = join(options.path, "%s.stats" % arg)
        stats = Stats(stats_path)

        if options.sort:
            stats.sort_stats(options.sort)

        print("Context")
        print("-" * 80)
        print(pprint(context))
        print()
        print("Profile")
        print("-" * 80)
        stats.print_stats(options.top or None)

