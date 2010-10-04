#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
import cherrypy
from cgi import parse_qs, escape
from urllib import urlencode

def get_state(**kwargs):
    state = parse_qs(cherrypy.request.query_string)
    state.update(kwargs)
    
    for key, value in state.items():
        if value is None:
            del state[key]

    return state

def view_state(**kwargs):
    return urlencode(get_state(**kwargs), True)

def view_state_form(schema = None, **kwargs):

    form = []
    form_data = {}

    if schema:
        for name, member in schema.members().iteritems():
            if name in kwargs:
                values = kwargs[name]
                if not isinstance(values, list):
                    values = [values]
                form_data[name] = []
                for value in values:
                    form_data[name].append(member.serialize_request_value(value))
    else:
        form_data = get_state(**kwargs)

    for key, values in form_data.iteritems():
        if values is not None:
            for value in values:
                form.append(
                    "<input type='hidden' name='%s' value='%s'>"
                    % (key, escape(value))
                )

    return "\n".join(form)

