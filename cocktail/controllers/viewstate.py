#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
import cherrypy
from cgi import parse_qs
from urllib import urlencode
from cocktail.html.utils import escape_attrib
from cocktail.controllers.sessions import session

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
                    '<input type="hidden" name="%s" value="%s">'
                    % (key, escape_attrib(value))
                )

    return "\n".join(form)

def _view_state_session_key(id):
    if id is None:
        id = cherrypy.request.path_info
    return u"view_state:%s" % id

def save_view_state(view_state_id = None):
    session_key = _view_state_session_key(view_state_id)
    session[session_key] = cherrypy.request.query_string

def restore_view_state(view_state_id = None, **kwargs):
    session_key = _view_state_session_key(view_state_id)    
    qs = session.get(session_key)
    state = parse_qs(qs) if qs else {}
    state.update(kwargs)
    return state

def saved_query_string(view_state_id = None, **kwargs):
    state = restore_view_state(view_state_id, **kwargs)
    return u"?" + view_state(**state)

