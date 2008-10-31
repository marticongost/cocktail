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

def parse_int(self, reader, value):
    try:
        value = int(value)
    except ValueError:
        pass

    return value

schema.Integer.parse_request_value = parse_int

def parse_boolean(self, reader, value):
    
    vl = value.lower()
    
    if vl in ("true", "1", "on"):
        value = True
    elif vl in ("false", "0", "off"):
        value = False

    return value
        
schema.Boolean.parse_request_value = parse_boolean

def parse_collection(self, reader, value):
    
    if isinstance(value, basestring):         
        value = reader.split_collection(self, value)
    elif not value:
        return self.produce_default()

    collection_type = self.default_type or type or list

    return collection_type(
        reader.process_value(self.items, part) for part in value
    )
    
schema.Collection.parse_request_value = parse_collection

NORMALIZATION_DEFAULT = strip
STRICT_DEFAULT = True
ENABLED_DEFAULTS_DEFAULT = True
IMPLICIT_BOOLEANS_DEFAULT = True

def get_parameter(
    member,
    target = None,
    languages = None,
    normalization = NORMALIZATION_DEFAULT,
    strict = STRICT_DEFAULT,
    enable_defaults = ENABLED_DEFAULTS_DEFAULT,
    implicit_booleans = IMPLICIT_BOOLEANS_DEFAULT,
    form_source = None):
    """Retrieves and processes a request parameter, or a tree or set of
    parameters, given a schema description. The function either returns the
    obtained value, or sets it on an indicated object, as established by the
    L{target} parameter.

    The function is just a convenience wrapper for the L{FormSchemaReader}
    class. Using the class directly is perfectly fine, and allows a greater
    deal of customization through subclassing.

    @param member: The schema member describing the nature of the value to
        retrieve, which will be used to apply the required processing to turn
        the raw data supplied by the request into a value of the given type.
    @type member: L{Member<cocktail.schema.member.Member>}

    @param target: If supplied, the read member will be set on the given
        object.

    @param languages: A collection of languages (ISO codes) to read the
        parameter in. If this parameter is set and the read member is not
        translatable a X{ValueError} exception will be raised.

        If the read member is a schema, the returned schema instance will
        contain translations for all the indicated languages. Otherwise, the
        function will return a (language => value) dictionary.

    @type languages: str collection
    
    @param normalization: A function that will be called to normalize data read
        from the request, before handling it to the member's parser. It must
        receive a single parameter (the piece of data to normalize) and return
        the modified result. It won't be called if the requested parameter is
        missing or empty. The default behavior is to strip whitespace
        characters from the beginning and end of the read value.
    @type normalization: callable(str) => str

    @param strict: Determines if values should be validated against their
        member's constraints, and discarded if found to be invalid.
    @type: bool

    @param enable_defaults: A flag that indicates if missing values should be
        replaced with the default value for their member (this is the default
        behavior).
    @type enable_defaults: bool

    @param implicit_booleans: A flag that indicates if a missing boolean
        parameter should assume a value of 'False'. This is the default
        behavior, and it's useful when dealing with HTML checkbox controls,
        which aren't submitted when not checked.
    @type implicit_booleans: bool

    @param form_source: By default, all parameters are read from the current
        cherrypy request (which includes both GET and POST parameters), but
        this can be overriden through this parameter. The only requirement for
        the specified source of data is that it define a get() method, behaving
        in exactly the same manner as the homonymous dictionary method.

    @return: The requested value, or None if the request doesn't provide a
        matching value for the indicated member, or it is empty.
        
        The function will try to coerce request parameters into an instance of
        an adequate type, through the L{parse_request_value<cocktail.schema.member.Member>}
        method of the supplied member. Member constraints (max value, minimum
        length, etc) will also be tested against the obtained value. If the
        L{strict} parameter is set to True, values that don't match their
        member's type or requirements will be discarded, and None will be
        returned instead. When L{strict} is False, invalid values are returned
        unmodified.
        
        By default, reading a schema will produce a dictionary with all its
        values. Reading a translated member will produce a dictionary with
        language/value pairs.
    """
    reader = FormSchemaReader(
        normalization = normalization,
        strict = strict,
        enable_defaults = enable_defaults,
        implicit_booleans = implicit_booleans,
        form_source = form_source
    )
    return reader.read(member, target, languages)


class FormSchemaReader(object):
    """
    A class that encapsulates the retrireval and processing of one or more
    parameters from a submitted form.

    The class provides many hooks to allow subclasses to refine or alter
    several different points of the parameter processing pipeline.

    @ivar normalization: A function that will be called to normalize data read
        from the request, before handling it to the member's parser. It must
        receive a single parameter (the piece of data to normalize) and return
        the modified result. It won't be called if the requested parameter is
        missing or empty. The default behavior is to strip whitespace
        characters from the beginning and end of the read value.
    @type normalization: callable(str) => str

    @ivar enable_defaults: A flag that indicates if missing values should be
        replaced with the default value for their member (this is the default
        behavior).
    @type enable_defaults: bool

    @ivar implicit_booleans: A flag that indicates if a missing boolean
        parameter should assume a value of 'False'. This is the default
        behavior, and it's useful when dealing with HTML checkbox controls,
        which aren't submitted when not checked.
    @type implicit_booleans: bool

    @ivar form_source: By default, all parameters are read from the current
        cherrypy request (which includes both GET and POST parameters), but
        this can be overriden through this attribute. The only requirement for
        the specified source of data is that it define a get() method, behaving
        in exactly the same manner as the homonymous dictionary method.
    """

    def __init__(self,
        normalization = NORMALIZATION_DEFAULT,
        strict = STRICT_DEFAULT,
        enable_defaults = ENABLED_DEFAULTS_DEFAULT,
        implicit_booleans = IMPLICIT_BOOLEANS_DEFAULT,
        form_source = None):

        self.normalization = normalization
        self.strict = strict
        self.enable_defaults = enable_defaults
        self.implicit_booleans = implicit_booleans

        if form_source is None:
            form_source = cherrypy.request.params

        self.form_source = form_source

    def read(self,
        member,
        target = None,
        languages = None,
        path = None):
        """Retrieves and processes a request parameter, or a tree or set of
        parameters, given a schema description. The method either returns the
        obtained value, or sets it on an indicated object, as established by
        the L{target} parameter.

        @param member: The schema member describing the nature of the value to
            retrieve, which will be used to apply the required processing to
            turn the raw data supplied by the request into a value of the given
            type.
        @type member: L{Member<cocktail.schema.member.Member>}

        @param languages: A collection of languages (ISO codes) to read the
            parameter in. If this parameter is set and the read member is not
            translatable a X{ValueError} exception will be raised.

            If the read member is a schema, the returned schema instance will
            contain translations for all the indicated languages. Otherwise,
            the function will return a (language => value) dictionary.

        @type languages: str collection
        
        @param target: If supplied, the read member will be set on the given
            object.

        @return: The requested value, or None if the request doesn't provide a
            matching value for the indicated member, or it is empty.
            
            The function will try to coerce request parameters into an instance
            of an adequate type, through the L{parse_request_value<cocktail.schema.member.Member>}
            method of the supplied member. Member constraints (max value,
            minimum length, etc) will also be tested against the obtained
            value. If the L{strict} parameter is set to True, values that don't
            match their member's type or requirements will be discarded, and
            None will be returned instead. When L{strict} is False, invalid
            values are returned unmodified.
            
            By default, reading a schema will produce a dictionary with all its
            values. Reading a translated member will produce a dictionary with
            language/value pairs.
        """
        if path is None:
            path = []

        if self._is_schema(member):
            return self._read_schema(member, target, languages, path)

        elif languages:

            if not member.translated:
                raise ValueError(
                    "Trying to read values translated into %s for non "
                    "translatable member %s"
                    % (languages, member)
                )
            
            if target is None:
                target = {}

            for language in languages:
                self._read_value(member, target, language, path)

            return target

        else:
            return self._read_value(member, target, None, path)
    
    def _read_value(self,
        member,
        target,
        language,
        path):
 
        key = self.get_key(member, language, path)
        value = self.form_source.get(key)
        value = self.process_value(member, value)
        
        if self.strict and not member.validate(value):
            value = None

        if target is not None:
            schema.set(target, member.name, value, language)

        return value

    def _is_schema(self, member):
        return isinstance(member, schema.Schema) \
            and not isinstance(member, schema.BaseDateTime)

    def _read_schema(self,
        member,
        target,
        languages,
        path):
     
        if target is None:
            target = {}

        path.append(member)

        try:
            for child_member in member.members().itervalues():

                if self._is_schema(child_member):
                    nested_target = self.create_nested_target(
                        member,
                        child_member,
                        target)
                    schema.set(target, child_member.name, nested_target)
                else:
                    nested_target = target

                value = self.read(
                    child_member,
                    nested_target,
                    languages if child_member.translated else None,
                    path)
        finally:
            path.pop()
            
        return target

    def get_key(self, member, language = None, path = None):
        
        name = member.name

        if language:
            name += "-" + language

        if path and len(path) > 1:
            path_name = ".".join(self.get_key(step) for step in path[1:])
            name = path_name + "-" + name
        
        return name

    def process_value(self, member, value):

        if value == "":
            value = None

        if value is not None:

            if self.normalization:
                value = self.normalization(value)

            if value == "":
                value = None

            if value is not None and member.parse_request_value:
                value = member.parse_request_value(self, value)
            
        if value is None:
            if self.implicit_booleans and isinstance(member, schema.Boolean):
                value = False
            elif self.enable_defaults:
                value = member.produce_default()

        return value

    def normalization(self, value):
        return strip(value)

    def get_request_params(self):
        return cherrypy.request.params

    def split_collection(self, member, value):
        return value.split(",")

    def create_nested_target(self, member, child_member, target):
        return {}

