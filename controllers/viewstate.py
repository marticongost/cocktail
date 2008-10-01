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

def get_persistent_param(param_name, cookie_name = None, cookie_duration = -1):

    param_value = cherrypy.request.params.get(param_name)

    if cookie_name is None:
        cookie_name = param_name

    request_cookie = cherrypy.request.cookie.get(cookie_name)

    if param_value is None:
        if request_cookie:
            param_value = request_cookie.value
    else:
        cherrypy.response.cookie[cookie_name] = (
            param_value
            if isinstance(param_value, basestring)
            else ",".join(param_value)
        )
        response_cookie = cherrypy.response.cookie[cookie_name]
        response_cookie["max-age"] = cookie_duration

    return param_value

