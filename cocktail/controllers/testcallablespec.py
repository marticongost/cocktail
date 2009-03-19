#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
import cherrypy

def test_callable_spec(callable, callable_args, callable_kwargs):
    """
    Inspect callable and test to see if the given args are suitable for it.

    When an error occurs during the handler's invoking stage there are 2
    erroneous cases:
    1.  Too many parameters passed to a function which doesn't define
        one of *args or **kwargs.
    2.  Too little parameters are passed to the function.

    There are 3 sources of parameters to a cherrypy handler.
    1.  query string parameters are passed as keyword parameters to the handler.
    2.  body parameters are also passed as keyword parameters.
    3.  when partial matching occurs, the final path atoms are passed as
        positional args.
    Both the query string and path atoms are part of the URI.  If they are
    incorrect, then a 404 Not Found should be raised. Conversely the body
    parameters are part of the request; if they are invalid a 400 Bad Request.
    """
    (args, varargs, varkw, defaults) = inspect.getargspec(callable)

    if args and args[0] == 'self':
        args = args[1:]

    arg_usage = dict([(arg, 0,) for arg in args])
    vararg_usage = 0
    varkw_usage = 0
    extra_kwargs = set()

    for i, value in enumerate(callable_args):
        try:
            arg_usage[args[i]] += 1
        except IndexError:
            vararg_usage += 1

    for key in callable_kwargs.keys():
        try:
            arg_usage[key] += 1
        except KeyError:
            varkw_usage += 1
            extra_kwargs.add(key)

    for i, val in enumerate(defaults or []):
        # Defaults take effect only when the arg hasn't been used yet.
        if arg_usage[args[i]] == 0:
            arg_usage[args[i]] += 1

    missing_args = []
    multiple_args = []
    for key, usage in arg_usage.iteritems():
        if usage == 0:
            missing_args.append(key)
        elif usage > 1:
            multiple_args.append(key)

    if missing_args:
        # In the case where the method allows body arguments
        # there are 3 potential errors:
        # 1. not enough query string parameters -> 404
        # 2. not enough body parameters -> 400
        # 3. not enough path parts (partial matches) -> 404
        #
        # We can't actually tell which case it is, 
        # so I'm raising a 404 because that covers 2/3 of the
        # possibilities
        # 
        # In the case where the method does not allow body
        # arguments it's definitely a 404.
        raise cherrypy.HTTPError(404,
                message="Missing parameters: %s" % ",".join(missing_args))

    # the extra positional arguments come from the path - 404 Not Found
    if not varargs and vararg_usage > 0:
        raise cherrypy.HTTPError(404)

    body_params = cherrypy.request.body_params or {}
    body_params = set(body_params.keys())
    qs_params = set(callable_kwargs.keys()) - body_params

    if multiple_args:

        if qs_params.intersection(set(multiple_args)):
            # If any of the multiple parameters came from the query string then
            # it's a 404 Not Found
            error = 404
        else:
            # Otherwise it's a 400 Bad Request
            error = 400

        raise cherrypy.HTTPError(error,
                message="Multiple values for parameters: "\
                        "%s" % ",".join(multiple_args))

    if not varkw and varkw_usage > 0:

        # If there were extra query string parameters, it's a 404 Not Found
        extra_qs_params = set(qs_params).intersection(extra_kwargs)
        if extra_qs_params:
            raise cherrypy.HTTPError(404,
                message="Unexpected query string "\
                        "parameters: %s" % ", ".join(extra_qs_params))

        # If there were any extra body parameters, it's a 400 Not Found
        extra_body_params = set(body_params).intersection(extra_kwargs)
        if extra_body_params:
            raise cherrypy.HTTPError(400,
                message="Unexpected body parameters: "\
                        "%s" % ", ".join(extra_body_params))

try:
    import inspect
except ImportError:
    test_callable_spec = lambda callable, args, kwargs: None

# Monkey patching for the CherryPy dispatcher:
if not hasattr(cherrypy._cpdispatch, "test_callable_spec"):
    cherrypy._cpdispatch.test_callable_spec = test_callable_spec

