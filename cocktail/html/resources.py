#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
try:
    from io import StringIO
except ImportError:
    from io import StringIO

try:
    import sass
except ImportError as sass_import_error:
    sass = None

import os
import re
import hashlib
import urllib.request, urllib.error, urllib.parse
from threading import local
from shutil import copyfileobj
from urllib.parse import urljoin
from warnings import warn
import mimetypes
import cherrypy
from cocktail.pkgutils import resource_filename
from cocktail.modeling import (
    abstractmethod,
    InstrumentedOrderedSet,
    DictWrapper
)
from cocktail.events import Event, EventInfo

_thread_data = local()

def get_theme():
    return getattr(_thread_data, "theme", "default")

def set_theme(theme):
    _thread_data.theme = theme or "default"


class SASSCompilation(object):

    validating_theme = Event()
    custom_functions = {}

    class ResolvingImportEventInfo(EventInfo):

        uri = None
        path = None
        code = None
        source_map = None

        def add_code(self, code):
            if self.code is None:
                self.code = [code]
            else:
                self.code.append(code)

        @property
        def resolution(self):

            if self.path:
                resolution = [self.path]
            elif self.code:
                resolution = [self.uri]
            else:
                return None

            if self.code is not None:
                resolution.append("".join(self.code))

                if self.source_map:
                    resolution.append(self.source_map)

            return [tuple(resolution)]

    resolving_import = Event(event_info_class = ResolvingImportEventInfo)

    def __init__(self, theme = None):

        if theme is None:
            theme = get_theme()

        if theme != "default":
            theme_is_valid = self.validating_theme(
                theme = theme,
                valid = False
            ).valid
            if not theme_is_valid:
                raise InvalidSASSTheme(theme)

        self.__imported_uris = set()
        self.__theme = theme

    @property
    def theme(self):
        return self.__theme

    def compile(self, **kwargs):

        if sass is None:
            raise sass_import_error

        importers = kwargs.get("importers")
        if importers is None:
            importers = []
            kwargs["importers"] = importers

        importers.insert(0, (0, self.resolve_import))

        custom_functions = self.custom_functions
        extra_custom_functions = kwargs.get("custom_functions")
        if extra_custom_functions is not None:
            custom_functions = custom_functions.copy()
            custom_functions.update(extra_custom_functions)

        kwargs["custom_functions"] = custom_functions
        return sass.compile(**kwargs)

    def resolve_import(self, uri):

        # Prevent importing dependencies more than once
        if uri in self.__imported_uris:
            return ((uri, ""),)
        else:
            self.__imported_uris.add(uri)

        e = self.resolving_import(uri = uri, theme = self.__theme)
        resolution = e.resolution

        if resolution is None:
            if resource_repositories.is_repository_uri(uri):

                if not uri.endswith(".scss"):
                    uri += ".scss"

                location = resource_repositories.locate(uri)
                if os.path.exists(location):
                    resolution = ((location,),)
                else:
                    path, file_name = os.path.split(location)
                    resolution = ((os.path.join(path, "_" + file_name),),)

        return resolution


class InvalidSASSTheme(Exception):

    def __init__(self, theme):
        Exception.__init__(self, "%r is not a valid theme identifier" % theme)
        self.__theme = theme

    @property
    def theme(self):
        return self.__theme


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
        if not uri:
            raise ValueError("Can't create a resource with an empty URI")

        self.__uri = resource_repositories.normalize_uri(uri)
        self.__mime_type = mime_type or self.default_mime_type
        self.__source_mime_type = source_mime_type or self.__mime_type
        self.__ie_condition = ie_condition
        self.__set = set

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.__uri)

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
            for extension, resource_type in cls.extensions.items():
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
            if isinstance(url_processor, str):
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

    def define(self, repository_name, root_uri, repository_path):
        self._items[repository_name] = (root_uri, repository_path)

    def locate(self, resource):

        file_path = None

        if isinstance(resource, Resource):
            if resource.file_path:
                return resource.file_path
            resource_uri = resource.uri
        else:
            resource_uri = resource
            resource = None

        if not resource_uri:
            return None

        qs_pos = resource_uri.rfind("?")
        if qs_pos != -1:
            resource_uri = resource_uri[:qs_pos]

        hash_pos = resource_uri.rfind("#")
        if hash_pos != -1:
            resource_uri = resource_uri[:hash_pos]

        if "://" in resource_uri:
            scheme, resource_uri = resource_uri.split("://")
            repo = self.get(scheme)

            if repo:
                file_path = os.path.join(
                    repo[1],
                    *resource_uri.strip("/").split("/")
                )
            else:
                return None

        if not file_path:

            resource_uri = resource_uri.strip("/")
            resource_uri_components = resource_uri.split("/")

            for repo_uri, repo_path in self.values():
                repo_uri_components = repo_uri.strip("/").split("/")
                if (
                    resource_uri_components[:len(repo_uri_components)]
                    == repo_uri_components
                ):
                    file_path = os.path.join(
                        repo_path,
                        *resource_uri_components[len(repo_uri_components):]
                    )
                    break

        if resource:
            resource.file_path = file_path

        return file_path

    def normalize_uri(self, uri):

        # Resolve custom URI schemes
        if "://" in uri:
            scheme, resource_path = uri.split("://", 1)
            repo = self.get(scheme)
            if repo:
                uri = repo[0] + "/" + resource_path

        # Inject the active theme into SASS URIs
        sass_suffix = ".scss.css"
        if uri.endswith(sass_suffix):
            uri = "%s.%s.scss.css" % (uri[:-len(sass_suffix)], get_theme())

        return uri

    def is_repository_uri(self, uri):

        if "://" in uri:
            scheme, uri = uri.split("://", 1)
            return scheme in self

        return False


resource_repositories = ResourceRepositories()

resource_repositories.define(
    "cocktail",
    "/resources/cocktail",
    resource_filename("cocktail.html", "resources")
)

SASSCompilation.custom_functions["url"] = \
    lambda url: 'url("%s")' % resource_repositories.normalize_uri(url)

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
        elif isinstance(mime_type, str):
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

        for key, value in kwargs.items():
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
        return buffer.getvalue()

    def get_resource_source(self, resource):
        buffer = StringIO()
        self.write_resource_source(resource, buffer)
        return buffer.getvalue()

    def write_source(self, dest):
        for resource in self:
            self.write_resource_source(resource, dest)
            dest.write(self.file_glue)

    def write_resource_source(self, resource, dest):

        try:
            src_file = self.open_resource(resource)
        except ResourceNotFound as e:
            src_file = e.path

        file_pub = self.file_publication
        if not file_pub:
            from cocktail.controllers.filepublication \
                import file_publication as file_pub

        file_info = file_pub.produce_file(src_file, resource.source_mime_type)
        file = file_info["file"]

        if file is None:
            return

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
            try:
                return open(resource_file_path)
            except IOError:
                raise ResourceNotFound(resource, resource_file_path)

        # Download remote resources
        if self.download_remote_resources:
            url = resource.uri
            if "://" not in url:
                from cocktail.controllers import get_request_root_url
                url = get_request_root_url().merge(url)
            request = urllib.request.Request(url)
            request.add_header("User-Agent", self.http_user_agent)
            return urllib.request.urlopen(request)

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

    def changed(self, added, changed, context):
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


class ResourceNotFound(Exception):

    def __init__(self, resource, path = None):
        self.resource = resource
        self.path = path

