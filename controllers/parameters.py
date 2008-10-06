#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from string import strip
from cocktail import schema

# Extension property that allows members to define a parser function for
# request values
schema.Member.parse_request_value = None

def parse_int(self, value):
    try:
        value = int(value)
    except ValueError:
        pass

    return value

schema.Integer.parse_request_value = parse_int

def parse_boolean(self, value):
    
    vl = value.lower()
    
    if vl in ("true", "1", "on"):
        value = True
    elif vl in ("false", "0", "off"):
        value = False

    return value
        
schema.Boolean.parse_request_value = parse_boolean

def read_form(form_schema, target = None, normalization = strip):
    
    params = cherrypy.request.params

    if target is None:
        target = {}
        accessor = schema.DictAccessor
    else:
        accessor = schema.get_accessor(target)

    for member in form_schema.members().itervalues():

        # TODO: Translated members

        value = params.get(member.name)

        if value == "":
            value = None

        if value is not None:

            if normalization:
                value = normalization(value)

            if value == "":
                value = None

            if value is not None and member.parse_request_value:
                value = member.parse_request_value(value)
        
        accessor.set(target, member.name, value)

    return target

