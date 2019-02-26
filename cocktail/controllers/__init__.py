#-*- coding: utf-8 -*-
"""Utilities for writing application controllers.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .request import (
    get_request_url,
    get_request_query,
    get_request_root_url,
    get_request_url_builder,
    get_request_root_url_builder
)
from .requestproperty import (
    request_property,
    clear_request_properties
)
from .requesthandler import RequestHandler
from .filepublication import FilePublication, file_publication
from .static import (
    file_publisher,
    folder_publisher,
    serve_file
)
from .controller import Controller
from .httpmethodcontroller import HTTPMethodController
from .formprocessor import FormProcessor, Form
from .dispatcher import (
    Dispatcher,
    StopRequest,
    context
)
from cocktail.controllers.redirection import (
    redirect,
    reload_request_url,
    post_redirection
)
from cocktail.controllers.parameters import (
    serialize_parameter,
    get_parameter,
    resolve_object_ref,
    FormSchemaReader,
    CookieParameterSource,
    SessionParameterSource
)
from .pagination import Pagination
from .fileupload import FileUpload
from .sessions import session
from .cached import Cached
from .csrfprotection import (
    CSRFProtection,
    CSRFTokenError,
    get_csrf_protection,
    set_csrf_protection
)
from .jsonutils import json_out, read_json

import cherrypy

def apply_forwarded_url_scheme():

    forwarded_scheme = cherrypy.request.headers.get('X-Forwarded-Scheme')

    if forwarded_scheme:
        scheme, rest = cherrypy.request.base.split("://")
        cherrypy.request.base = '%s://%s' % (forwarded_scheme, rest)

cherrypy.request.hooks.attach("on_start_resource", apply_forwarded_url_scheme)

# Make the autoreloading mechanism in the CherryPy server observe .strings
# files
from cocktail.events import when
from cocktail.translations import translations

@when(translations.bundle_loaded)
def track_bundle_files(e):
    cherrypy.engine.autoreload.files.add(e.file_path)

