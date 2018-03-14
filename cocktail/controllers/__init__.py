#-*- coding: utf-8 -*-
u"""
Utilities for writing application controllers.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from .request import (
    get_request_url,
    get_request_root_url,
    get_request_url_builder,
    get_request_root_url_builder
)
from cocktail.controllers.requestproperty import (
    request_property,
    clear_request_properties
)
from cocktail.controllers.requesthandler import RequestHandler
from cocktail.controllers.filepublication import (
    FilePublication,
    file_publication
)
from cocktail.controllers.static import (
    file_publisher,
    folder_publisher,
    serve_file
)
from cocktail.controllers.controller import Controller
from cocktail.controllers.httpmethodcontroller import HTTPMethodController
from cocktail.controllers.formprocessor import FormProcessor, Form
from cocktail.controllers.formcontrollermixin import FormControllerMixin
from cocktail.controllers.dispatcher import (
    Dispatcher,
    StopRequest,
    context
)
from cocktail.controllers.uriutils import (
    make_uri,
    try_decode,
    percent_encode_uri
)
from cocktail.controllers.redirection import (
    redirect,
    reload_request_url,
    post_redirection
)
from cocktail.controllers.location import Location
from cocktail.controllers.viewstate import (
    get_state,
    view_state,
    view_state_form,
    save_view_state,
    restore_view_state,
    saved_query_string
)
from cocktail.controllers.parameters import (
    serialize_parameter,
    get_parameter,
    resolve_object_ref,
    FormSchemaReader,
    CookieParameterSource,
    SessionParameterSource
)
from cocktail.controllers.pagination import Pagination
from cocktail.controllers.usercollection import UserCollection
from cocktail.controllers.fileupload import FileUpload
from cocktail.controllers.sessions import session
import cocktail.controllers.grouping
import cocktail.controllers.erroremail
import cocktail.controllers.handlerprofiler
from .csrfprotection import (
    CSRFProtection,
    CSRFTokenError,
    get_csrf_protection,
    set_csrf_protection
)

# The ZODB debugger needs collections.Counter, and therefore is not available
# under Python 2.6
try:
    import cocktail.controllers.zodbdebuggertool
except ImportError:
    pass

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

