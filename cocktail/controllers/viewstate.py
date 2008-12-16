#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
import cherrypy
from cgi import parse_qs
from urllib import urlencode, quote

def get_state(**kwargs):
    state = parse_qs(cherrypy.request.query_string)
    state.update(kwargs)
    
    for key, value in state.items():
        if value is None:
            del state[key]

    return state

def view_state(**kwargs):
    return urlencode(get_state(**kwargs), True)

def view_state_form(**kwargs):

    form = []

    for key, values in get_state(**kwargs).iteritems():
        if values is not None:
            for value in values:
                form.append(
                    "<input type='hidden' name='%s' value='%s'>"
                    % (key, quote(value))
                )

    return "\n".join(form)

def get_persistent_param(param_name,
    cookie_name = None,
    cookie_duration = -1,
    cookie_path = "/",
    ignore_new = False,
    update = True):

    if ignore_new:
        param_value = None
    else:
        param_value = cherrypy.request.params.get(param_name)

    if cookie_name is None:
        cookie_name = param_name

    # Persist a new value
    if param_value:
        if update:
            cherrypy.response.cookie[cookie_name] = (
                param_value
                if isinstance(param_value, basestring)
                else ",".join(param_value)
            )
            response_cookie = cherrypy.response.cookie[cookie_name]
            response_cookie["max-age"] = cookie_duration
            response_cookie["path"] = cookie_path
    else:
        request_cookie = cherrypy.request.cookie.get(cookie_name)

        if request_cookie:

            # Delete a persisted value
            if param_value == "":
                if update:
                    del cherrypy.request.cookie[cookie_name]
                    cherrypy.response.cookie[cookie_name] = ""
                    response_cookie = cherrypy.response.cookie[cookie_name]
                    response_cookie["max-age"] = 0
                    response_cookie["path"] = cookie_path

            # Restore a persisted value
            else:
                param_value = request_cookie.value

    return param_value

