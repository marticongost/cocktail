#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import os
import re
import hashlib
import urllib2
from shutil import copyfileobj
from urlparse import urljoin
from warnings import warn
import mimetypes
from pkg_resources import resource_filename
import cherrypy
from cocktail.modeling import (
    abstractmethod,
    InstrumentedOrderedSet,
    DictWrapper
)


class Resource(object):

    default_mime_type = None
    mime_types = {}
    extensions = {}
    file_path = None

    def __init__(
        self,
        uri,
        mime_type = None,
        source_mime_type = None,
        ie_condition = None,
        set = None
    ):
        self.__uri = uri
        self.__mime_type = mime_type or self.default_mime_type
        self.__source_mime_type = source_mime_type or self.__mime_type
        self.__ie_condition = ie_condition
        self.__set = set

    @classmethod
    def from_uri(
        cls,
        uri,
        mime_type = None,
        source_mime_type = None,
        ie_condition = None,
        **kwargs
    ):
        resource_type = None

        # By mime type
        if mime_type:
            resource_type = cls.mime_types.get(mime_type)

        # By extension
        else:
            for extension, resource_type in cls.extensions.iteritems():
                if uri.endswith(extension):
                    break
            else:
                resource_type = None

        if resource_type is None:
            raise ValueError(
                "Error handling resource: URI=%s, mime-type=%s"
                % (uri, mime_type)
            )

        if source_mime_type is None:
            source_mime_type = mimetypes.guess_type(uri)[0]

        return resource_type(
            uri,
            mime_type = mime_type,
            source_mime_type = source_mime_type,
            ie_condition = ie_condition,
            **kwargs
        )

    @property
    def uri(self):
        return self.__uri

    @property
    def mime_type(self):
        return self.__mime_type

    @property
    def source_mime_type(self):
        return self.__source_mime_type

    @property
    def ie_condition(self):
        return self.__ie_condition

    @property
    def set(self):
        return self.__set

    def __hash__(self):
        return hash(self.uri + self.mime_type + (self.ie_condition or ""))

    def __eq__(self, other):
        return self.__class__ is other.__class__ \
           and self.uri == other.uri \
           and self.mime_type == other.mime_type \
           and self.ie_condition == other.ie_condition

    @abstractmethod
    def link(self, document, url_processor = None):
        pass

    def _process_url(self, url, url_processor):
        if url_processor is not None:
            if isinstance(url_processor, basestring):
                url = url_processor % url
            elif callable(url_processor):
                url = url_processor(url)
            else:
                raise ValueError("Bad URL processor: %r" % url_processor)

        return url

    @abstractmethod
    def embed(self, document):
        pass


class Script(Resource):
    default_mime_type = "text/javascript"
    mode = "block"

    def __init__(self,
        uri,
        mime_type = None,
        source_mime_type = None,
        ie_condition = None,
        set = None,
        async = None
    ):
        Resource.__init__(self,
            uri,
            mime_type = mime_type,
            source_mime_type = source_mime_type,
            ie_condition = ie_condition
        )
        if async is not None:
            self.async = async

    def link(self, document, url_processor = None):
        from cocktail.html.element import Element

        link = Element("script")
        link["type"] = self.mime_type
        link["src"] = self._process_url(self.uri, url_processor)

        if self.mode == "async":
            link["async"] = True
        elif self.mode == "defer":
            link["defer"] = True
        elif self.mode != "block":
            raise ValueError(
                "Invalid mode for %r; expected 'block', 'async' or 'defer', "
                "got %r instead"
                % (self, self.mode)
            )

        if self.ie_condition:
            from cocktail.html.ieconditionalcomment import IEConditionalComment
            link = IEConditionalComment(self.ie_condition, children = [link])

        document.scripts_container.append(link)
        return link

    def embed(self, document, source):
        from cocktail.html.element import Element
        embed = Element("script")
        embed["type"] = self.mime_type
        embed.append("\n//<![CDATA[\n" + source + "\n//]]>\n")

        if self.ie_condition:
            from cocktail.html.ieconditionalcomment import IEConditionalComment
            embed = IEConditionalComment(self.ie_condition, children = [embed])

        document.scripts_container.append(embed)
        return embed

    def _get_async(self):
        warn(
            "Script.async is deprecated in favor of Script.mode",
            DeprecationWarning,
            stacklevel = 2
        )
        return self.mode == "async"

    def _set_async(self, async):
        self.mode = "async" if async else "block"

    async = property(_get_async, _set_async)


class StyleSheet(Resource):
    default_mime_type = "text/css"

    def link(self, document, url_processor = None):
        from cocktail.html.element import Element

        link = Element("link")
        link["rel"] = "Stylesheet"
        link["type"] = self.mime_type
        link["href"] = self._process_url(self.uri, url_processor)

        if self.ie_condition:
            from cocktail.html.ieconditionalcomment import IEConditionalComment
            link = IEConditionalComment(self.ie_condition, children = [link])

        document.styles_container.append(link)
        return link

    def embed(self, document, source):
        from cocktail.html.element import Element

        embed = Element("style")
        embed["type"] = self.mime_type
        embed.append("\n/*<![CDATA[*/\n" + source + "\n/*]]>*/\n")

        if self.ie_condition:
            from cocktail.html.ieconditionalcomment import IEConditionalComment
            embed = IEConditionalComment(self.ie_condition, children = [embed])

        document.styles_container.append(embed)
        return embed


Resource.extensions[".js"] = Script
Resource.extensions[".css"] = StyleSheet
Resource.extensions[".scss"] = StyleSheet
Resource.mime_types["text/javascript"] = Script
Resource.mime_types["text/css"] = StyleSheet
Resource.mime_types["text/sass"] = StyleSheet


class ResourceRepositories(DictWrapper):

    def define(self, repository_name, uri_pattern, repository_path):

        if isinstance(uri_pattern, basestring):
            pattern_components = uri_pattern.strip("/").split("/")
            size = len(pattern_components)
            def matcher(components):
                if components[:size] == pattern_components:
                    return components[size:]
        elif callable(uri_pattern):
            matcher = uri_pattern
        else:
            raise TypeError(
                "Resource repository patterns must be specified using a "
                "string or a callable; got %s instead"
                % type(uri_pattern)
            )

        self._items[repository_name] = (matcher, repository_path)

    def locate(self, resource):

        if isinstance(resource, Resource):
            if resource.file_path:
                return resource.file_path
            resource_uri = resource.uri
        else:
            resource_uri = resource
            resource = None

        if not resource_uri or "://" in resource_uri:
            return None

        qs_pos = resource_uri.rfind("?")
        if qs_pos != -1:
            resource_uri = resource_uri[:qs_pos]

        hash_pos = resource_uri.rfind("#")
        if hash_pos != -1:
            resource_uri = resource_uri[:hash_pos]

        resource_uri = resource_uri.strip("/")
        resource_path_components = resource_uri.split("/")
        file_path = None

        for match_repository_uri, repository_path in self.itervalues():
            match = match_repository_uri(resource_path_components)
            if match is not None:
                file_path = os.path.join(repository_path, *match)
                break

        if resource:
            resource.file_path = file_path

        return file_path

resource_repositories = ResourceRepositories()

resource_repositories.define(
    "cocktail",
    "/cocktail",
    resource_filename("cocktail.html", "resources")
)

# Resource sets
#------------------------------------------------------------------------------
# TODO: minification, source maps

default = object()


class ResourceSet(InstrumentedOrderedSet):

    __name = None
    _default_mime_type = None

    def __init__(self,
        resources = None,
        name = None,
        mime_type = default,
        switch_param = None,
        **kwargs
    ):
        self.__name = name

        if mime_type is default:
            mime_type = self._default_mime_type

        self.__mime_type = mime_type

        if mime_type is None:
            self._match_mime_type = lambda mime_type: True
        elif isinstance(mime_type, basestring):
            self._match_mime_type = mime_type.__eq__
        elif callable(mime_type):
            self._match_mime_type = mime_type
        elif hasattr(mime_type, "__contains__"):
            self._match_mime_type = mime_type.__contains__
        else:
            raise TypeError(
                "Bad value for ResourceSet.mime_type. Expected a string "
                "(exact match), a callable (predicate) or a collection "
                "(multiple choices)"
            )

        self.switch_param = switch_param
        InstrumentedOrderedSet.__init__(self, resources)

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    @classmethod
    def with_config(cls, **kwargs):
        def factory():
            return cls(**kwargs)
        return factory

    @property
    def name(self):
        return self.__name

    @property
    def mime_type(self):
        return self.__mime_type

    def matches(self, resource):
        return (
            self._match_mime_type(resource.mime_type)
            and (not resource.set or resource.set == self.__name)
            and (
                not self.switch_param
                or cherrypy.request.params.get(self.switch_param, "on")
                   != "off"
            )
        )

    @abstractmethod
    def insert_into_document(self, document):
        pass


class LinkedResources(ResourceSet):

    url_processor = None

    def insert_into_document(self, document):
        for resource in self:
            resource.link(document, url_processor = self.url_processor)


class ResourceAggregator(ResourceSet):

    source_encoding = "utf-8"
    file_glue = "\n"
    download_remote_resources = False
    base_url = None
    http_user_agent = "cocktail.html.ResourceAggregator"
    file_publication = None

    def __init__(self, **kwargs):
        ResourceSet.__init__(self, **kwargs)
        self.processors = []

    def matches(self, resource):
        return (
            ResourceSet.matches(self, resource)
            and (
                self.download_remote_resources
                or resource_repositories.locate(resource)
            )
        )

    def get_source(self):
        buffer = StringIO()
        self.write_source(buffer)
        source = buffer.getvalue()

        if self.source_encoding:
            return source.decode(self.source_encoding)
        else:
            return source

    def get_resource_source(self, resource):
        buffer = StringIO()
        self.write_resource_source(resource, buffer)
        source = buffer.getvalue()

        if self.source_encoding:
            return source.decode(self.source_encoding)
        else:
            return source

    def write_source(self, dest):
        for resource in self:
            self.write_resource_source(resource, dest)
            dest.write(self.file_glue)

    def write_resource_source(self, resource, dest):

        try:
            src_file = self.open_resource(resource)
        except IOError:
            return

        file_pub = self.file_publication
        if not file_pub:
            from cocktail.controllers.filepublication \
                import file_publication as file_pub

        file_info = file_pub.produce_file(src_file, resource.source_mime_type)
        file = file_info["file"]

        if self.processors:
            buffer = StringIO()
            copyfileobj(file, buffer)
            for processor in self.processors:
                buffer = processor(resource, buffer)
            file = buffer

        # Copy the file, stripping source map information
        lines = file.readlines()

        if lines:
            if lines[-1].startswith("/*# sourceMappingURL="):
                lines.pop(-1)
            for line in lines:
                dest.write(line)

    def open_resource(self, resource):

        # Look for a local file
        resource_file_path = resource_repositories.locate(resource)
        if resource_file_path:
            return open(resource_file_path)

        # Download remote resources
        if self.download_remote_resources:
            url = resource.uri
            if "://" not in url:
                base_url = self.base_url
                if not base_url:
                    from cocktail.controllers.location import Location
                    base_url = unicode(Location.get_current_host())
                url = base_url + url
            request = urllib2.Request(url)
            request.add_header("User-Agent", self.http_user_agent)
            return urllib2.urlopen(request)

        raise ValueError("Can't open %r" % resource)


class EmbeddedResources(ResourceAggregator):

    def insert_into_document(self, document):
        for resource in self:
            source = self.get_resource_source(resource)
            resource.embed(document, source)


class ResourceBundle(ResourceAggregator):

    __hash = None
    hash_algorithm = hashlib.md5
    custom_file_identifier = None
    revision = None
    file_extension = ""
    base_uri = None
    __base_path = None
    expiration_check = True

    def matches(self, resource):
        return (
            not resource.ie_condition
            and ResourceAggregator.matches(self, resource)
        )

    def changed(self, added = (), removed = ()):
        self.__hash = None

    @property
    def hash(self):
        if self.__hash is None:
            resource_list = ";".join(resource.uri for resource in self)
            self.__hash = self.hash_algorithm(resource_list).hexdigest()
        return self.__hash

    @property
    def file_name(self):
        name = self.custom_file_identifier or self.hash

        if self.revision is not None:
            name += "-" + str(self.revision)

        if self.file_extension:
            name += self.file_extension

        return name

    @property
    def file_path(self):
        return os.path.join(self.base_path, self.file_name)

    @property
    def uri(self):
        if self.base_uri is None:
            return None
        else:
            return self.base_uri.rstrip("/") + "/" + self.file_name

    def _get_base_path(self):
        if self.__base_path is None and self.base_uri:
            return resource_repositories.locate(self.base_uri)
        else:
            return self.__base_path

    def _set_base_path(self, value):
        self.__base_path = value

    base_path = property(_get_base_path, _set_base_path)

    def write(self):
        with open(self.file_path, "w") as f:
            self.write_source(f)

    def update(self):
        if self.needs_update():
            self.write()

    def needs_update(self):

        if not self.expiration_check:
            return not os.path.exists(self.file_path)

        try:
            bundle_mtime = os.stat(self.file_path).st_mtime
        except OSError:
            return True
        else:
            for resource in self:
                resource_path = resource_repositories.locate(resource)
                try:
                    resource_mtime = os.stat(resource_path).st_mtime
                except OSError:
                    pass
                else:
                    if resource_mtime > bundle_mtime:
                        return True

            return False

    def insert_into_document(self, document):
        if self:
            self.update()
            resource = Resource.from_uri(self.uri, mime_type = self.mime_type)
            resource.link(document)


class ScriptBundle(ResourceBundle):
    file_extension = ".js"
    file_glue = "\n;\n"
    _default_mime_type = "text/javascript"


class StyleBundle(ResourceBundle):

    file_extension = ".css"
    _default_mime_type = "text/css"

    url_re = re.compile(
        r"""
        url\(\s*
        (?P<url>
            '[^']+' # URL surrounded by single quotes
          | "[^"]+" # URL surrounded by double quotes
          |  [^)]+  # URL with no quotes
        )
        \)
        """,
        re.VERBOSE
    )

    def __init__(self, **kwargs):
        ResourceBundle.__init__(self, **kwargs)
        self.processors.append(self.fix_urls)

    def fix_urls(self, resource, buffer):

        def fix_url(match):
            url = match.group("url").strip("'").strip('"').strip()
            if "://" not in url:
                url = urljoin(resource.uri, url)
            return "url(%s)" % url

        buffer.seek(0)
        css = buffer.read()
        css = self.url_re.sub(fix_url, css)

        buffer.seek(0)
        buffer.truncate()
        buffer.write(css)
        buffer.seek(0)
        return buffer


class ExcludedResources(ResourceSet):

    def insert_into_document(self, document):
        pass

