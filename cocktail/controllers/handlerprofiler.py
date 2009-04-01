#-*- coding: utf-8 -*-
u"""
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
from os.path import join
import cherrypy

_lock = Lock()
_request_id = 0

def handler_profiler(stats_path = None):

    handler = cherrypy.request.handler

    def profiled_handler(*args, **kwargs):
        
        global _request_id

        # Acquire a unique identifier for the request
        if stats_path:
            _lock.acquire()
            try:
                _request_id += 1
                id = _request_id
            finally:
                _lock.release()

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
        try:
            runctx(
                "rvalue = handler(*args, **kwargs)",
                globals(),
                local_context,
                join(stats_path, "%s.stats" % id) if stats_path else None
            )

        # Store request data, to match profiler stats against their context
        finally:
            if stats_path:
                f = open(join(stats_path, "%s.context" % id), "w")
                try:
                    request_context = {
                        "path_info": cherrypy.request.path_info,
                        "query_string": cherrypy.request.query_string,
                        "headers": cherrypy.request.headers,
                        "args": args,
                        "kwargs": kwargs
                    }
                    f.write(dumps(request_context))
                finally:
                    f.close()

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
        
        print "Context"
        print "-" * 80
        print pprint(context)
        print
        print "Profile"
        print "-" * 80
        stats.print_stats(options.top or None)

