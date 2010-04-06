#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import decimal
import time
import datetime
import cherrypy
from cherrypy.lib import http
from string import strip
from cocktail import schema
from cocktail.persistence import PersistentClass
from cocktail.schema.schemadates import Date, DateTime, Time
from cocktail.translations import get_language
from cocktail.translations.translation import translations
from cocktail.controllers.fileupload import FileUpload

def serialize_parameter(member, value):
    if value is None:
        return ""
    else:
        return member.serialize_request_value(value)

# Extension property that allows members to define a parser function for
# request values
schema.Member.parse_request_value = None

# Extension property that allows members to define a serializer function for
# request values
schema.Member.serialize_request_value = unicode

# Extension property that allows members to define a reader function for
# request values
schema.Member.read_request_value = None

def parse_int(self, reader, value):

    if value is not None:
        try:
            value = int(value)
        except ValueError:
            pass

    return value

schema.Integer.parse_request_value = parse_int

def parse_decimal(self, reader, value):

    if value is not None:
        parser = translations("Decimal parser")

        try:
            value = parser(value)
        except ValueError:
            pass

    return value

schema.Decimal.parse_request_value = parse_decimal

def parse_date(self, reader, value):
    
    if value is not None:
        format = translations("date format")
            
        try:
            value = datetime.date(*time.strptime(value[:10], format)[0:3])
        except ValueError:
            pass

    return value

def serialize_date(self, value):
    format = translations("date format")    
    return value.strftime(format)

Date.parse_request_value = parse_date
Date.serialize_request_value = serialize_date

def parse_datetime(self, reader, value):
    
    if value is not None:
        date_format = translations("date format")
        time_format = "%H:%M:%S"
        try:
            value = datetime.datetime.strptime(
                value,
                date_format + " " + time_format
            )
        except ValueError:
            try:
                value = datetime.datetime.strptime(value, date_format)
            except:
                pass

    return value

def serialize_datetime(self, value):
    format = translations("date format") + " %H:%M:%S"
    return value.strftime(format)

DateTime.parse_request_value = parse_datetime
DateTime.serialize_request_value = serialize_datetime

def parse_time(self, reader, value):

    if value is not None:
        try:
            value = datetime.time(*time.strptime(value, "%H:%M:%S")[3:6])
        except ValueError:
            pass
    
    return value

def serialize_time(self, value):
    return value.strftime("%H:%M:%S")

schema.Time.parse_request_value = parse_time
schema.Time.serialize_request_value = serialize_time

def parse_boolean(self, reader, value):
    
    if value is not None:

        vl = value.lower()
        
        if vl in ("true", "1", "on"):
            value = True
        elif vl in ("false", "0", "off"):
            value = False

    return value
        
schema.Boolean.parse_request_value = parse_boolean

def parse_reference(self, reader, value):

    if value is not None:
        related_type = self.type

        # Class references
        if self.class_family:
            for cls in self.class_family.schema_tree():
                if cls.full_name == value:
                    value = cls
                    break

        # TODO: make this extensible to other types?
        elif isinstance(related_type, PersistentClass) \
        and related_type.indexed:
            value = related_type.index.get(int(value))
    
    return value

def serialize_reference(self, value):

    # TODO: make this extensible to other types?
    if isinstance(self.type, PersistentClass) \
    and self.type.primary_member:
        value = str(value.get(self.type.primary_member))
    else:
        value = str(value)

    return value

schema.Reference.parse_request_value = parse_reference
schema.Reference.serialize_request_value = serialize_reference

def parse_collection(self, reader, value):
    
    if not value:
        return self.produce_default()

    elif isinstance(value, basestring):         
        value = reader.split_collection(self, value)

    collection_type = self.type or self.default_type or list

    return collection_type(
        [reader.process_value(self.items, part) for part in value]
    )

def serialize_collection(self, value):

    if not value:
        return ""
    else:
        items = self.items
        serialize_item = self.items \
            and self.items.serialize_request_value \
            or unicode
        return ", ".join(serialize_item(item) for item in value)

schema.Collection.parse_request_value = parse_collection
schema.Collection.serialize_request_value = serialize_collection

NORMALIZATION_DEFAULT = strip
STRICT_DEFAULT = True
SKIP_UNDEFINED_DEFAULT = False
ENABLED_DEFAULTS_DEFAULT = True
IMPLICIT_BOOLEANS_DEFAULT = True

def get_parameter(
    member,
    target = None,
    languages = None,
    normalization = NORMALIZATION_DEFAULT,
    strict = STRICT_DEFAULT,
    skip_undefined = SKIP_UNDEFINED_DEFAULT,
    enable_defaults = ENABLED_DEFAULTS_DEFAULT,
    implicit_booleans = IMPLICIT_BOOLEANS_DEFAULT,
    prefix = None,
    suffix = None,
    source = None):
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

    @param skip_undefined: Determines the treatment received by members defined
        by the retrieved schema that aren't given an explicit value by the
        request. The default value, False, sets those members to either None or
        its default value, depending on the value of L{enable_defaults}. When
        set to True, members with no value specified will be ignored. This
        allows updating objects selectively.
    @type skip_undefined: bool

    @param enable_defaults: A flag that indicates if missing values should be
        replaced with the default value for their member (this is the default
        behavior).
    @type enable_defaults: bool

    @param implicit_booleans: A flag that indicates if missing required boolean
        parameters should assume a value of 'False'. This is the default
        behavior, and it's useful when dealing with HTML checkbox controls,
        which aren't submitted when not checked.
    @type implicit_booleans: bool

    @param source: By default, all parameters are read from the current
        cherrypy request (which includes both GET and POST parameters), but
        this can be overriden through this parameter. Should be set to a
        callable that takes the name of a parameter and returns its raw
        value, or None if the parameter can't be retrieved.
    @type source: callable

    @param prefix: A string that will be added at the beginning of the
        parameter name for each retrieved member.
    @type prefix: str

    @param suffix: A string that will be appended at the end of the parameter
        name for each retrieved member.
    @type suffix: str

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
        skip_undefined = skip_undefined,
        enable_defaults = enable_defaults,
        implicit_booleans = implicit_booleans,
        prefix = prefix,
        suffix = suffix,
        source = source
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

    @ivar implicit_booleans: A flag that indicates if missing required boolean
        parameters should assume a value of 'False'. This is the default
        behavior, and it's useful when dealing with HTML checkbox controls,
        which aren't submitted when not checked.
    @type implicit_booleans: bool

    @param prefix: A string that will be added at the beginning of the
        parameter name for each retrieved member.
    @type prefix: str

    @param suffix: A string that will be appended at the end of the parameter
        name for each retrieved member.
    @type suffix: str
    
    @ivar source: By default, all parameters are read from the current
        cherrypy request (which includes both GET and POST parameters), but
        this can be overriden through this attribute. Should be set to a
        callable that takes a the name of a parameter and returns its raw
        value, or None if the parameter can't be retrieved.
    @type source: callable
    """

    def __init__(self,
        normalization = NORMALIZATION_DEFAULT,
        strict = STRICT_DEFAULT,
        skip_undefined = SKIP_UNDEFINED_DEFAULT,
        enable_defaults = ENABLED_DEFAULTS_DEFAULT,
        implicit_booleans = IMPLICIT_BOOLEANS_DEFAULT,
        prefix = None,
        suffix = None,
        source = None):

        self.normalization = normalization
        self.strict = strict
        self.skip_undefined = skip_undefined
        self.enable_defaults = enable_defaults
        self.implicit_booleans = implicit_booleans
        self.prefix = prefix
        self.suffix = suffix

        if source is None:
            source = cherrypy.request.params.get

        self.source = source

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
 
        if member.read_request_value:
            value = member.read_request_value(self)
        else:
            key = self.get_key(member, language, path)
            value = self.source(key)

        if not (value is None and self.skip_undefined):
            value = self.process_value(member, value)
            
            if self.strict and not member.validate(value):
                value = None

            if target is not None:
                schema.set(target, member.name, value, language)

        return value

    def _is_schema(self, member):
        return isinstance(member, schema.Schema) \
            and not isinstance(member, schema.BaseDateTime) \
            and not isinstance(member, FileUpload)

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
        
        name = member if isinstance(member, basestring) else member.name

        if language:
            name += "-" + language

        if path and len(path) > 1:
            path_name = ".".join(self.get_key(step) for step in path[1:])
            name = path_name + "-" + name

        if self.prefix:
            name = self.prefix + name

        if self.suffix:
            name += self.suffix

        return name

    def process_value(self, member, value):

        if value == "":
            value = None

        if value is not None:

            if self.normalization and not isinstance(member, FileUpload):
                if isinstance(value, basestring):
                    value = self.normalization(value)
                else:
                    value = [self.normalization(part) for part in value]

            if value == "":
                value = None

        if member.parse_request_value:
            value = member.parse_request_value(self, value)
            
        if value is None:
            if self.implicit_booleans \
            and member.required \
            and isinstance(member, schema.Boolean):
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


def set_cookie_expiration(cookie, seconds=None):
    """ Sets the 'max-age' and 'expires' attributes for generated cookies.
        Setting it to None produces session cookies. 
    """

    if seconds is not None:
        cookie["max-age"] = seconds

        if seconds == 0:
            cookie["expires"] = http.HTTPDate(                                                                                                                                            
                time.time() - (60 * 60 * 24 * 365)
            )
        else:
            cookie["expires"] = http.HTTPDate(
                time.time() + seconds
            )


class CookieParameterSource(object):
    """A cookie based persistent source for parameters, used in conjunction
    with L{get_parameter} or L{FormSchemaReader}.

    @param source: The parameter source that provides updated values for
        requested parameters. Defaults to X{cherrypy.request.params.get}.
    @type source: callable

    @param cookie_duration: Sets the 'max-age' and 'expires' attributes for 
        generated cookies. Setting it to None produces session cookies.
    @type cookie_duration: int

    @param cookie_naming: A formatting string used to determine the name of
        parameter cookies.
    @type cookie_naming: str

    @param cookie_prefix: A string to prepend to parameter names when
        determining the name of the cookie for a parameter. This is useful to
        qualify parameters or constrain them to a certain context. If set to
        None, cookie names will be the same as the name of their parameter.
    @type cookie_prefix: str

    @param cookie_encoding: The encoding to use when encoding and decoding
        cookie values.
    @type: str

    @param cookie_path: The path for generated cookies.
    @type cookie_path: str

    @param ignore_new_values: When set to True, updated values from the
        L{source} callable will be ignored, and only existing values persisted
        on cookies will be taken into account. 
    @type ignore_new_values: bool

    @param update: Indicates if new values from the L{source} callable should
        update the cookie for the parameter.
    @type update: bool
    """
    source = None
    cookie_duration = None,
    cookie_naming = "%(prefix)s%(name)s"
    cookie_prefix = None,
    cookie_encoding = "utf-8"
    cookie_path = "/"
    ignore_new_values = False,
    update = True

    def __init__(self,
        source = None,
        cookie_duration = None,
        cookie_naming = "%(prefix)s%(name)s",
        cookie_prefix = None,
        cookie_encoding = "utf-8",
        cookie_path = "/",
        ignore_new_values = False,
        update = True):

        self.source = source
        self.cookie_duration = cookie_duration
        self.cookie_naming = cookie_naming
        self.cookie_prefix = cookie_prefix
        self.cookie_encoding = cookie_encoding
        self.cookie_path = cookie_path
        self.ignore_new_values = ignore_new_values
        self.update = update

    def __call__(self, param_name):
        
        if self.ignore_new_values:
            param_value = None
        else:
            source = self.source
            if source is None:
                source = cherrypy.request.params.get
            param_value = source(param_name)
        
        cookie_name = self.get_cookie_name(param_name)

        # Persist a new value
        if param_value:
            if self.update:
                if not isinstance(param_value, basestring):
                    param_value = u",".join(param_value)

                if isinstance(param_value, unicode) and self.cookie_encoding:
                    cookie_value = param_value.encode(self.cookie_encoding)
                else:
                    cookie_value = param_value

                cherrypy.response.cookie[cookie_name] = cookie_value
                response_cookie = cherrypy.response.cookie[cookie_name]
                set_cookie_expiration(response_cookie, seconds = self.cookie_duration)
                response_cookie["path"] = self.cookie_path
        else:
            request_cookie = cherrypy.request.cookie.get(cookie_name)

            if request_cookie:

                # Delete a persisted value
                if param_value == "":
                    if self.update:
                        del cherrypy.request.cookie[cookie_name]
                        cherrypy.response.cookie[cookie_name] = ""
                        response_cookie = cherrypy.response.cookie[cookie_name]
                        set_cookie_expiration(response_cookie, seconds = 0)
                        response_cookie["path"] = self.cookie_path

                # Restore a persisted value
                else:
                    param_value = request_cookie.value

                    if param_value and self.cookie_encoding:
                        param_value = param_value.decode(self.cookie_encoding)
                
        return param_value

    def get_cookie_name(self, param_name):
        """Determines the name of the cookie used to persist a parameter.
        
        @param param_name: The name of the persistent parameter.
        @type param_name: str

        @return: The name for the cookie.
        @rtype: str
        """        
        if self.cookie_naming:
            prefix = self.cookie_prefix
            return self.cookie_naming % {
                "prefix": prefix + "-" if prefix else "",
                "name": param_name
            }
        else:
            return param_name

