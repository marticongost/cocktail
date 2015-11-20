#-*- coding: utf-8 -*-
u"""Serve static files.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from mimetypes import guess_type
import cherrypy
from cherrypy.lib.static import serve_file as cp_serve_file
from cocktail.modeling import DictWrapper
from cocktail.preprocessing import preprocessors

def file_publisher(path, content_type = None, disposition = None, name = None):
    """Creates a CherryPy handler that serves the specified file."""

    @cherrypy.expose
    def handler(self):
        return serve_file(path, content_type, disposition, name)

    return handler

class FolderPublisher(object):
    """Creates a CherryPy handler that serves files in the specified folder."""

    def __init__(self, path):
        self.path = path

    @cherrypy.expose
    def __call__(self, *args, **kwargs):

        requested_path = self.path

        for arg in args:
            requested_path = os.path.join(requested_path, arg)

        # Prevent serving files outside the specified root path
        if not os.path.normpath(requested_path) \
        .startswith(os.path.normpath(self.path)):
            raise cherrypy.HTTPError(403)

        return serve_file(requested_path)

    default = __call__

folder_publisher = FolderPublisher

def serve_file(
    path,
    content_type = None,
    disposition = None,
    name = None
):
    """Serve the indicated file to the current HTTP request."""

    if not disposition:
        disposition = "inline"

    if disposition not in ("inline", "attachment"):
        raise ValueError(
            "disposition must be either 'inline' or 'attachment', not '%s'"
            % disposition
        )

    output = preprocessors.preprocess(path)

    if output:
        mime_type, source = output
        cherrypy.response.headers["Content-Type"] = mime_type
        cherrypy.response.headers["Content-Disposition"] = \
            "%s; filename=%s" % (disposition, name)
        return source

    return cp_serve_file(path, content_type, disposition, name)


class CantHandleFile(Exception):
    """An exception raised by a MIME type file handler to indicate it cedes
    control back to the default static file publisher.
    """

