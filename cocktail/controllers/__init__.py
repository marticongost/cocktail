#-*- coding: utf-8 -*-
u"""
Utilities for writing application controllers.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.controllers.requestproperty import request_property
from cocktail.controllers.requesthandler import RequestHandler
from cocktail.controllers.static import (
    file_publisher, 
    folder_publisher,
    serve_file
)
from cocktail.controllers.controller import Controller
from cocktail.controllers.formprocessor import FormProcessor, Form
from cocktail.controllers.formcontrollermixin import FormControllerMixin
from cocktail.controllers.dispatcher import (
    Dispatcher,
    StopRequest,
    context
)
from cocktail.controllers.uriutils import make_uri, try_decode
from cocktail.controllers.location import Location
from cocktail.controllers.viewstate import (
    get_state,
    view_state,
    view_state_form
)
from cocktail.controllers.parameters import (
    serialize_parameter, get_parameter, FormSchemaReader, CookieParameterSource
)
from cocktail.controllers.pagination import Pagination
from cocktail.controllers.usercollection import UserCollection
from cocktail.controllers.fileupload import FileUpload
import cocktail.controllers.grouping
import cocktail.controllers.erroremail
import cocktail.controllers.handlerprofiler
import cocktail.controllers.switchhandler


import cherrypy

def apply_forwarded_url_scheme():

    forwarded_scheme = cherrypy.request.headers.get('X-Forwarded-Scheme')

    if forwarded_scheme:
        scheme, rest = cherrypy.request.base.split("://")
        cherrypy.request.base = '%s://%s' % (forwarded_scheme, rest)

cherrypy.request.hooks.attach("on_start_resource", apply_forwarded_url_scheme)
