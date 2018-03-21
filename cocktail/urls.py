#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import Iterable, Mapping, OrderedDict
from itertools import izip
from urllib import quote, unquote, unquote_plus
from urlparse import urlparse
from frozendict import frozendict

ENCODING = "utf-8"
RESERVED_CHARACTERS = ";/?:@&=+$,"
UNRESERVED_CHARACTERS = "-_.!~*'()"

_hierarchical_schemes = {"http", "https", "ftp"}

_path_safe_characters = {
    "http": "/",
    "https": "/",
    "ftp": "/"
}

def _decode(string):
    try:
        return string.decode("utf-8")
    except UnicodeDecodeError, e:
        try:
            return string.decode("latin-1")
        except UnicodeDecodeError:
            raise e


class URL(unicode):

    def __new__(cls, url = None, **values):

        if url:
            if isinstance(url, cls):
                # Init from an existing object
                if values:
                    values.setdefault("scheme", url.__scheme)
                    values.setdefault("hostname", url.__hostname)
                    values.setdefault("username", url.__username)
                    values.setdefault("password", url.__password)
                    values.setdefault("port", url.__port)
                    values.setdefault("path", url.__path)
                    values.setdefault("query", url.__query)
                    values.setdefault("fragment", url.__fragment)

                # Exact copy: return the same object
                else:
                    return url

            # Parse an URL string
            elif isinstance(url, unicode):
                parts = urlparse(url)
                values.setdefault("scheme", parts.scheme)
                values.setdefault("hostname", parts.hostname)
                values.setdefault("username", parts.username)
                values.setdefault("password", parts.password)
                values.setdefault("port", parts.port)
                values.setdefault("path", parts.path)
                values.setdefault("query", parts.query)
                values.setdefault("fragment", parts.fragment)

            # Decode byte strings
            elif isinstance(url, str):
                return cls.__new__(cls, _decode(unquote(url)))

            else:
                raise ValueError(
                    "Can't create an URL from %r; "
                    "Expected a unicode string, byte string or URL object."
                    % url
                )

        scheme = values.get("scheme")
        hostname = values.get("hostname") or u""
        username = values.get("username") or u""
        password = values.get("password") or u""

        port = values.get("port")
        if port and not isinstance(port, int):
            port = int(port)

        has_abs_components = (hostname or username or password or port)
        if not scheme and has_abs_components:
            scheme = u"http"

        path = Path(values.get("path"))
        if has_abs_components:
            path = path.make_absolute()

        query = QueryString(values.get("query"))
        fragment = values.get("fragment") or u""

        if scheme:
            url_string = scheme

            if scheme in _hierarchical_schemes:
                url_string += "://"
            else:
                url_string += ":"

            if username or password:
                if username:
                    url_string += username
                if password:
                    url_string += u":" + password
                url_string += u"@"

            if hostname:
                url_string += hostname

            if port:
                url_string += u":%d" % port
        else:
            url_string = u""

        if path:
            url_string += path

        if query:
            url_string += u"?" + query

        if fragment:
            url_string += u"#" + fragment

        obj = unicode.__new__(cls, url_string)
        obj.__scheme = scheme
        obj.__username = username
        obj.__password = password
        obj.__hostname = hostname
        obj.__port = port
        obj.__path = path
        obj.__query = query
        obj.__fragment = fragment
        return obj

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            unicode.__repr__(self)
        )

    def __str__(self):

        if self.__scheme:
            url_string = str(self.__scheme)

            if self.hierarchical:
                url_string += "://"
            else:
                url_string += ":"

            if self.__username or self.__password:
                if self.__username:
                    url_string += self.__username.encode(ENCODING)
                if password:
                    url_string += ":" + self.__password.encode(ENCODING)
                url_string += "@"

            if self.__hostname:
                try:
                    url_string += self.__hostname.encode("ascii")
                except UnicodeEncodeError:
                    url_string += self.__hostname.encode("punycode")

            if self.__port:
                url_string += ":%d" % self.__port
        else:
            url_string = ""

        if self.__path:
            safe = _path_safe_characters.get(
                self.__scheme,
                RESERVED_CHARACTERS + UNRESERVED_CHARACTERS
            )
            url_string += quote(self.__path.encode(ENCODING), safe)

        if self.__query:
            url_string += "?" + str(self.__query)

        if self.__fragment:
            url_string += "#" + self.__fragment

        return url_string

    @property
    def scheme(self):
        return self.__scheme

    @property
    def hierarchical(self):
        return self.__scheme in _hierarchical_schemes

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def hostname(self):
        return self.__hostname

    @property
    def port(self):
        return self.__port

    @property
    def path(self):
        return self.__path

    @property
    def query(self):
        return self.__query

    @property
    def fragment(self):
        return self.__fragment

    def copy(self, **values):
        return self.__class__(self, **values)

    def merge(self, other):
        other = URL(other)
        return self.__class__(
            scheme = other.__scheme or self.__scheme,
            username = other.__username or self.__username,
            password = other.__password or self.__password,
            hostname = other.__hostname or self.__hostname,
            port = other.__port or self.__port,
            path = self.__path.merge(other.__path),
            query = self.__query.merge(other.__query),
            fragment = other.__fragment or self.__fragment
        )


class URLBuilder(object):

    url_class = URL
    path_is_relative = False

    def __init__(self,
        scheme = None,
        username = None,
        password = None,
        hostname = None,
        port = None,
        path_is_relative = None,
        path = None,
        query = None,
        fragment = None
    ):
        self.scheme = scheme
        self.username = username
        self.password = password
        self.hostname = hostname
        self.port = port
        self.path = path
        self.query = query
        self.fragment = None

        if path_is_relative is not None:
            self.path_is_relative = path_is_relative

    def _get_path(self):
        return self.__path

    def _set_path(self, path):
        if path is None:
            self.__path = []
        elif isinstance(path, Path):
            self.__path_is_relative = path.relative
            self.__path = list(path.segments)
        elif isinstance(path, basestring):
            self.__path_is_relative = not path.startswith("/")
            path = path.strip("/")
            self.__path = path.split("/") if path else []
        else:
            self.__path = list(path)

    path = property(_get_path, _set_path)

    def _get_query(self):
        return self.__query

    def _set_query(self, query):
        if query is None:
            self.__query = OrderedDict()
        elif isinstance(query, QueryString):
            self.__query = OrderedDict(query.fields)
        elif isinstance(query, basestring):
            self.__query = _parse_query_string(query, dict_type = OrderedDict)
        else:
            self.__query = OrderedDict(query)

    query = property(_get_query, _set_query)

    def get_url(self):
        prefix = u"" if self.path_is_relative else u"/"
        return self.url_class(
            scheme = self.scheme,
            username = self.username,
            password = self.password,
            hostname = self.hostname,
            port = self.port,
            path = prefix + u"/".join(
                self._normalize_path_component(item)
                for item in self.path
            ),
            query = self.query,
            fragment = self.fragment
        )

    def _normalize_path_component(self, component):
        if isinstance(component, int):
            return unicode(component)
        elif isinstance(component, str):
            return _decode(unquote(component))
        else:
            return component


class Path(unicode):

    def __new__(cls, path):

        if path is None:
            return cls(u"")

        elif isinstance(path, cls):
            return path

        elif isinstance(path, str):
            return cls(_decode(unquote(path)))

        elif isinstance(path, unicode):

            absolute = path.startswith("/")
            path = path.strip("/")
            segments = path.split("/") if path else []

            # Normalize the path
            norm_segments = []

            for segment in segments:
                if segment == ".":
                    continue
                elif segment == ".." and norm_segments:
                    norm_segments.pop(-1)
                else:
                    norm_segments.append(segment)

            path = "/".join(norm_segments)
            if absolute:
                path = "/" + path

            obj = unicode.__new__(cls, path)
            obj.__relative = not absolute
            obj.__segments = tuple(norm_segments)
            return obj

        elif isinstance(path, Iterable):
            return cls("/".join(path))

        else:
            raise ValueError(
                "Can't create an URL path from %r; "
                "Expected a unicode string, a byte string, a sequence of "
                "strings or a Path object."
                % path
            )

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            unicode.__repr__(self)
        )

    def __str__(self):
        return quote(self.encode(ENCODING))

    @property
    def segments(self):
        return self.__segments

    @property
    def relative(self):
        return self.__relative

    def make_absolute(self):
        if self.__relative:
            return self.__class__(u"/" + self)
        else:
            return self

    def append(self, other):

        path_str = str(self)

        if not isinstance(other, unicode):
            other = unicode(Path(other))

        return self.__class__(path_str + u"/" + other.lstrip(u"/"))

    def prepend(self, other):

        path_str = unicode(self)

        if not isinstance(other, unicode):
            other = unicode(Path(other))

        if not self.__relative and not other.startswith("/"):
            other = "/" + other

        return self.__class__(other + "/" + path_str.lstrip("/"))

    def __add__(self, other):
        return self.__class__(unicode(self) + unicode(other))

    def merge(self, other):

        other = Path(other)

        if other.relative:
            path = self
            if self.segments:
                path = self.pop()
            return path.append(other)
        else:
            return other

    def pop(self, index = -1):

        if not self.__segments:
            raise IndexError("Pop from empty Path")

        segments = list(self.__segments)
        segments.pop(index)
        if not self.__relative:
            segments.insert(0, "")

        return self.__class__(segments)

    def matches_prefix(self, prefix):

        prefix = Path(prefix)

        if not prefix.__relative and self.__relative:
            return False

        if len(prefix.__segments) > len(self.__segments):
            return False

        for a, b in izip(prefix.__segments, self.__segments):
            if a != b:
                return False

        return True

    def matches_suffix(self, suffix):

        suffix = Path(suffix)

        if not suffix.relative:
            return self == suffix

        if len(suffix.__segments) > len(self.__segments):
            return False

        for a, b in izip(
            reversed(suffix.__segments),
            reversed(self.__segments)
        ):
            if a != b:
                return False

        return True


class QueryString(unicode):

    def __new__(cls, query = None):

        # Empty query string
        if query is None or query == "":
            fields = {}
            query_string = ""

        # Reuse an existing query string object
        elif isinstance(query, cls):
            return query

        # Decode and parse byte strings
        elif isinstance(query, str):
            return cls.__new__(cls, _decode(query))

        # Parse unicode strings
        elif isinstance(query, unicode):
            query_string = unquote_plus(query.lstrip("?").lstrip("&"))
            fields = _parse_query_string(query_string)

        # Generate a query string from an ordered mapping
        elif isinstance(query, OrderedDict):
            fields = _normalize_query_string_mapping(query, OrderedDict)
            query_string = _join_query_string_values(fields)

        # Generate a query string from a mapping
        elif isinstance(query, Mapping):
            fields = _normalize_query_string_mapping(query)
            query_string = _join_query_string_values(fields)

        else:
            raise ValueError(
                "Can't create an URL query string from %r; "
                "Expected a unicode string, a byte string, a mapping or an "
                "QueryString instance."
                % query
            )

        obj = unicode.__new__(cls, query_string)
        obj.__fields = _normalize_query_string_mapping(fields, frozendict)
        return obj

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            unicode.__repr__(self)
        )

    def __str__(self):
        return quote(self.encode(ENCODING), "=&")

    def __add__(self, other):
        return self.__class__(unicode(self) + unicode(other))

    @property
    def fields(self):
        return self.__fields

    def get_value(self, key, default = None):
        values = self.__fields.get(key)
        if values is None:
            return default
        elif len(values) == 1:
            return values[0]
        else:
            return values

    def merge(self, query = None, **kwargs):

        if query is None and not kwargs:
            raise ValueError("Missing a merge operand")

        if query is None:
            merge = self
        else:
            a = _parse_query_string(unicode(self), OrderedDict)

            if isinstance(query, basestring):
                query_string = query
                if isinstance(query_string, str):
                    query_string = _decode(unquote(query_string))
                query_string = query_string.lstrip("?").lstrip("&")
                b = _parse_query_string(query_string, OrderedDict)
            elif isinstance(query, QueryString):
                b = query.__fields
            elif isinstance(query, Mapping):
                b = query
            else:
                raise ValueError(
                    "Invalid merge operand %r; expected a unicode string, a "
                    "byte string, a QueryString object or a mapping."
                    % query
                )

            a.update(b)

            for key, value in a.items():
                if value is None:
                    del a[key]

            merge = self.__class__(a)

        if kwargs:
            merge = merge.merge(kwargs)

        return merge

    def extend(self, query):
        query = self.__class__(query)

        if self and query:
            return self.__class__(unicode(self) + u"&" + unicode(query))
        else:
            return self or query


def _normalize_query_string_value(value):
    if isinstance(value, str):
        return (_decode(unquote(value)),)
    elif isinstance(value, unicode):
        return (value,)
    elif isinstance(value, int):
        return (str(value),)
    elif isinstance(value, Iterable):
        return tuple(
            (
                _decode(unquote(item))
                if isinstance(item, str)
                else item
            )
            for item in value
        )
    else:
        raise ValueError(
            "Can't use %r as a field value; expected a unicode string, "
            "a byte string or an iterable of strings."
            % value
        )

def _normalize_query_string_mapping(mapping, dict_type = dict):
    return dict_type(
        (
            key,
            _normalize_query_string_value(value)
        )
        for key, value in mapping.iteritems()
        if value is not None
    )

def _join_query_string_values(values):
    return u"&".join(
        u"&".join(
            u"%s=%s" % (key, item)
            for item in _normalize_query_string_value(value)
        )
        for key, value in values.iteritems()
    )

def _parse_query_string(query_string, dict_type = dict):

    if not query_string:
        return dict_type()

    query_string = query_string
    fields = dict_type()

    for field_str in query_string.split("&"):

        parts = field_str.split("=", 1)
        if len(parts) == 1:
            key = parts[0]
            value = ""
        else:
            key, value = parts

        if key in fields:
            fields[key] += (value,)
        else:
            fields[key] = (value,)

    return fields

