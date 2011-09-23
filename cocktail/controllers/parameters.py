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
import cgi
import cherrypy
from cherrypy.lib import http
from string import strip
from cocktail.iteration import first
from cocktail import schema
from cocktail.persistence import PersistentClass
from cocktail.schema.schemadates import Date, DateTime, Time
from cocktail.translations import get_language
from cocktail.translations.translation import translations
from cocktail.controllers.sessions import session
from cocktail.controllers.fileupload import FileUpload

# Extension property that allows members to override the key that identifies
# them when retrieved as parameters in an HTTP request
schema.Member.parameter_name = None

def _get_parameter_name(self, language = None, prefix = None, suffix = None):
    
    parameter = self.parameter_name or self.name

    if parameter and self.schema and self.parameter_name_is_qualified:
        parameter = self.schema.get_parameter_name() + "." + parameter
        
    if language:
        parameter += "-" + language

    if prefix:
        parameter = prefix + parameter

    if suffix:
        parameter += suffix

    return parameter

schema.Member.get_parameter_name = _get_parameter_name

def _get_parameter_name_is_qualified(self):

    # By default, only members nested at two levels of depth or more use
    # qualified names as keys in HTTP requests
    if self._parameter_name_is_qualified is None:
        return self.schema is not None \
           and self.schema.schema is not None
        
    return self._parameter_name_is_qualified

def _set_parameter_name_is_qualified(self, value):
    self._parameter_name_is_qualified = value

schema.Member._parameter_name_is_qualified = None
schema.Member.parameter_name_is_qualified = property(
    _get_parameter_name_is_qualified,
    _set_parameter_name_is_qualified,
    doc = """Indicates if the name of the member when used as a parameter in an
    HTTP request or response should be qualified by the name of the schema it
    belongs to.
    """
)

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

def parse_float(self, reader, value):

    if value is not None:
        try:
            value = float(value)
        except ValueError:
            pass

    return value

schema.Float.parse_request_value = parse_float

def parse_decimal(self, reader, value):

    if value is not None:
        parser = translations("Decimal parser")

        try:
            value = parser(value)
        except ValueError:
            pass

    return value

schema.Decimal.parse_request_value = parse_decimal

try:
    from fractions import Fraction

    def parse_fraction(self, reader, value):
        if value is not None:
            try:
                value = Fraction(value)
            except ValueError:
                pass

        return value

    schema.Fraction.parse_request_value = parse_fraction
except ImportError:
    pass

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
        if self.required and reader.undefined != "set_default":
            return (self.type or self.default_type)()
        else:
            return None

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
        glue = getattr(self, "request_value_separator", ",")
        return glue.join(serialize_item(item) for item in value)

schema.Collection.parse_request_value = parse_collection
schema.Collection.serialize_request_value = serialize_collection

def parse_tuple(self, reader, value):

    if value is not None:
        separator = getattr(self, "request_value_separator", ",")
        chunks = value.split(separator)
        value = tuple(
            reader.process_value(member, chunk)
            for chunk, member in zip(chunks, self.items)
        )

    return value

def serialize_tuple(self, value):

    if not value:
        return ""
    else:
        glue = getattr(self, "request_value_separator", ",")
        return glue.join(
            member.serialize_request_value(item)
            for member, item in zip(self.items, value)
        )

schema.Tuple.parse_request_value = parse_tuple
schema.Tuple.serialize_request_value = serialize_tuple

NORMALIZATION_DEFAULT = strip
UNDEFINED_DEFAULT = "set_default"
ERRORS_DEFAULT = "set_none"
IMPLICIT_BOOLEANS_DEFAULT = True

def get_parameter(
    member,
    target = None,
    languages = None,
    normalization = NORMALIZATION_DEFAULT,
    undefined = UNDEFINED_DEFAULT,
    errors = ERRORS_DEFAULT,
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

        Can also accept a string, which will implicitly create a temporary
        `schema.String` member.

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

    @param errors: Specifies what should happen if the read value doesn't
        satisfy the constraints and validations set by the member. Can be set
        to any of the following string identifiers:

            set_none
                Incorrect values will be replaced with None. This is the
                default behavior.
            
            set_default
                Incorrect values will be replaced with their field's default 
                value.

            ignore
                No validations are executed, incorrect values are returned
                unmodified.

            raise
                As soon as an incorrect value is found, the first of its
                validation errors will be raised as an exception.
    
    @type errors: str

    @param undefined: Determines the treatment received by members defined by
        the retrieved schema that aren't given an explicit value by the
        request. Can take any of the following string identifiers:
            
            set_default
                Undefined values will be replaced by their member's default
                value. This is the default behavior.

            set_none
                Undefined values will be set to None.

            skip
                Undefined values will be reported as None, but won't modify the
                target object.        
    
    @type undefined: str

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
        method of the supplied member. Depending on the value of the L{errors}
        parameter, member constraints (max value, minimum length, etc) will
        also be tested against the obtained value. Validation errors can be
        ignored, raised as exceptions or used to set the retrieved value to
        None or to the member's specified default.
        
        By default, reading a schema will produce a dictionary or a
        L{SchemaObject<cocktail.schema.schemaobject.SchemaObject>} with all its
        values. Reading a translated member will produce a dictionary with
        language/value pairs.
    """
    reader = FormSchemaReader(
        normalization = normalization,
        errors = errors,
        undefined = undefined,
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

    @ivar errors: Specifies what should happen if the read value doesn't
        satisfy the constraints and validations set by the member. Can be set
        to any of the following string identifiers:
            
            set_none
                Incorrect values will be replaced with None. This is the
                default behavior.
            
            set_default
                Incorrect values will be replaced with their field's default 
                value.

            ignore
                No validations are executed, incorrect values are returned
                unmodified.

            raise
                As soon as an incorrect value is found, the first of its
                validation errors will be raised as an exception.
    
    @type errors: string

    @ivar undefined: Determines the treatment received by members defined by
        the retrieved schema that aren't given an explicit value by the
        request. Can take any of the following string identifiers:
            
            set_default
                Undefined values will be replaced by their member's default
                value. This is the default behavior.

            set_none
                Undefined values will be set to None.

            skip
                Undefined values will be reported as None, but won't modify the
                target object.        
    
    @type undefined: str

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
        errors = ERRORS_DEFAULT,
        undefined = UNDEFINED_DEFAULT,
        implicit_booleans = IMPLICIT_BOOLEANS_DEFAULT,
        prefix = None,
        suffix = None,
        source = None):

        self.normalization = normalization
        self.errors = errors
        self.undefined = undefined
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
            
            Can also accept a string, which will implicitly create a temporary
            `schema.String` member.

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
            method of the supplied member. Depending on the value of the L{errors}
            parameter, member constraints (max value, minimum length, etc) will
            also be tested against the obtained value. Validation errors can be
            ignored, raised as exceptions or used to set the retrieved value to
            None or to the member's specified default.
            
            By default, reading a schema will produce a dictionary or a
            L{SchemaObject<cocktail.schema.schemaobject.SchemaObject>} with all its
            values. Reading a translated member will produce a dictionary with
            language/value pairs.
        """
        if isinstance(member, basestring):
            member = schema.String(member)

        if path is None:
            path = []

        if self._is_schema(member):
            return self._read_schema(member, target, languages, path)

        elif languages is not None:

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
            key = self.get_parameter_name(member, language)
            value = self.source(key)

        if not (value is None and self.undefined == "skip"):
            value = self.process_value(member, value)

            if not path and self.errors != "ignore":
                value = self._fix_value(target, member, value)

            if target is not None:
                schema.set(target, member.name, value, language)

        return value

    def _fix_value(self, target, member, value, error = None):

        error = error or first(member.get_errors(value))

        if error:
            if self.errors == "raise":
                raise error
            elif self.errors == "set_none":
                value = None
            elif self.errors == "set_default":
                value = member.produce_default(target)

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
            if isinstance(member, type):
                target = member()
            else:
                target = {}

        path.append(member)

        try:
            for child_member in member.members().itervalues():

                if self._is_schema(child_member):
                    nested_target = schema.get(target, child_member, None)
                    if nested_target is None:
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

            # Validate child members *after* all members have read their values
            # (this allows conditional validations based on other members in 
            # the schema)
            if self.errors != "ignore":
                invalid_members = set()

                for error in member.get_errors(target):
                    error_member = error.member
                    if error_member not in invalid_members:
                        invalid_members.add(error_member)

                        if error.path:
                            error_target = error.path[-1][1]
                        else:
                            error_target = target

                        fixed_value = self._fix_value(
                            error_target, 
                            error_member,
                            error.value,
                            error
                        )
                        schema.set(
                            error_target, 
                            error_member.name, 
                            fixed_value
                        )
        finally:
            path.pop()
            
        return target

    def get_parameter_name(self, member, language = None):
        if isinstance(member, basestring):
            # TODO: supporting arbitrary strings here as well as members is
            # necessary for historical reasons, but should be removed sometime
            # in the future
            if language:
                member += "-" + language

            if self.prefix:
                member = self.prefix + member

            if self.suffix:
                member += self.suffix

            return member
        else:
            return member.get_parameter_name(
                language, 
                prefix = self.prefix,
                suffix = self.suffix
            )

    def process_value(self, member, value):

        if value == "":
            value = None

        if value is not None:

            if not isinstance(value, cgi.FieldStorage):
                for norm in [self.normalization, member.normalization]:
                    if norm: 
                        if isinstance(value, basestring):
                            value = norm(value)
                        else:
                            value = [norm(part) for part in value]

            if value == "":
                value = None

        if member.parse_request_value:
            value = member.parse_request_value(self, value)

        if value is None:
            if self.implicit_booleans \
            and member.required \
            and isinstance(member, schema.Boolean):
                value = False
            elif self.undefined == "set_default":
                value = member.produce_default()

        return value

    def normalization(self, value):
        return strip(value)

    def get_request_params(self):
        return cherrypy.request.params

    def split_collection(self, member, value):
        return value.split(getattr(member, "request_value_separator", ","))

    def create_nested_target(self, member, child_member, target):
        return {}


def set_cookie_expiration(cookie, seconds=None):
    """ Sets the 'max-age' and 'expires' attributes for generated cookies.
        Setting it to None produces session cookies. 
    """

    if seconds is None:
        for key in ("max-age", "expires"):
            try:
                del cookie[key]
            except KeyError:
                pass
    else:
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
    ignore_new_values = False
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


class SessionParameterSource(object):
    """A session based source for parameters, used in conjunction
    with L{get_parameter} or L{FormSchemaReader}.

    @param source: The parameter source that provides updated values for
        requested parameters. Defaults to X{cherrypy.request.params.get}.
    @type source: callable

    @param key_naming: A formatting string used to determine the key of
        the session for a parameter.
    @type key_naming: str

    @param key_prefix: A string to prepend to parameter names when
        determining the key of the session for a parameter. This is useful to
        qualify parameters or constrain them to a certain context. If set to
        None, session keys will be the same as the name of their parameter.
    @type key_prefix: str

    @param ignore_new_values: When set to True, updated values from the
        L{source} callable will be ignored, and only existing values stored
        on session will be taken into account. 
    @type ignore_new_values: bool

    @param update: Indicates if new values from the L{source} callable should
        update the session for the parameter.
    @type update: bool
    """
    source = None
    key_naming = "%(prefix)s%(name)s"
    key_prefix = None,
    ignore_new_values = False
    update = True

    def __init__(self,
        source = None,
        key_naming = "%(prefix)s%(name)s",
        key_prefix = None,
        ignore_new_values = False,
        update = True):

        self.source = source
        self.key_naming = key_naming
        self.key_prefix = key_prefix
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

        key = self.get_key(param_name)
        
        # Persist a new value
        if param_value:
            if self.update:
                if not isinstance(param_value, basestring):
                    param_value = u",".join(param_value)

                session[key] = param_value
        else:
            # Delete a persisted value
            if param_value == "":
                if self.update:
                    try:
                        del session[key]
                    except KeyError:
                        pass

            # Restore a persisted value
            else:
                param_value = session.get(key)

        return param_value

    def get_key(self, param_name):
        """Determines the name of the key used to persist a parameter.
        
        @param param_name: The name of the persistent parameter.
        @type param_name: str

        @return: The key.
        @rtype: str
        """        
        if self.key_naming:
            prefix = self.key_prefix
            return self.key_naming % {
                "prefix": prefix + "-" if prefix else "",
                "name": param_name
            }
        else:
            return param_name

