#-*- coding: utf-8 -*-
u"""
Utilities for writing application controllers.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.controllers.requesthandler import RequestHandler
from cocktail.controllers.controller import Controller
from cocktail.controllers.formprocessor import FormProcessor, Form
from cocktail.controllers.formcontrollermixin import FormControllerMixin
from cocktail.controllers.dispatcher import (
    Dispatcher,
    StopRequest,
    context
)
from cocktail.controllers.location import Location
from cocktail.controllers.viewstate import (
    get_state,
    view_state,
    view_state_form
)
from cocktail.controllers.parameters import (
    serialize_parameter, get_parameter, FormSchemaReader, CookieParameterSource
)
from cocktail.controllers.usercollection import UserCollection
from cocktail.controllers.fileupload import FileUpload
import cocktail.controllers.grouping
import cocktail.controllers.erroremail
import cocktail.controllers.handlerprofiler


def make_uri(*args, **kwargs):

    uri = u"/".join(unicode(arg).strip(u"/") for arg in args)

    if kwargs:
        params = []

        for pair in kwargs.iteritems():
            if isinstance(pair[1], basestring):
                params.append(pair)
            else:
                for item in pair[1]:
                    params.append(pair[0], item)

        uri += "?" + "&".join("%s=%s" % pair for pair in params.iteritems())

    return uri

