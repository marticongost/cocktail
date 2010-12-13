#-*- coding: utf-8 -*-
u"""Serve static files.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from mimetypes import guess_type
import cherrypy
from cherrypy.lib.static import serve_file as cp_serve_file
from cocktail.modeling import DictWrapper

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
    def __call__(self, *args):
        
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

content_type_handlers = DictWrapper()

def register_content_type_handler(content_type, handler):
    """Registers a function to serve files of the specified MIME type.

    :param content_type: The MIME type to register the function for. Can be a
        specific MIME type (ie. image/png, text/css) or a general MIME
        category (ie. image, text).
    :type content_type: str

    :param handler: The function that produces the output for files of the
        indicated MIME type. It should take two parameters: the path to the
        file to serve, and it's MIME type.
    :type handler: callable
    """
    content_type_handlers._items[content_type] = handler

def handles_content_type(content_type):
    """A convenience decorator that makes it easier to
    `register MIME type handlers<register_content_type_handler>`.
    """
    def decorator(function):
        register_content_type_handler(content_type, function)
        return function

    return decorator

def get_content_type_handler(content_type):
    """Get the handler for the specified MIME type.
    
    :param content_type: The MIME type to evaluate. Can be a specific MIME
        type (ie. image/png, text/css) or a general MIME category 
        (ie. image, text).
    :type content_type: str
    
    :return: The handler for the specified MIME type, or None if there is
        no registered handler for the specified type.
    :rtype: callable
    """
    handler = content_type_handlers.get(content_type)

    if handler is None:
        try:
            category, identifier = content_type.split("/")
        except:
            pass
        else:
            handler = content_type_handlers.get(category)

    return handler

def serve_file(
    path,
    content_type = None,
    disposition = None,
    name = None):
    """Serve the indicated file to the current HTTP request."""

    if not disposition:
        disposition = "inline"

    if disposition not in ("inline", "attachment"):
        raise ValueError(
            "disposition must be either 'inline' or 'attachment', not '%s'"
            % disposition
        )

    if content_type is None:
        content_type = guess_type(path, strict = False)[0]

    if content_type:
        handler = get_content_type_handler(content_type)
    
        if handler:
            if not name:
                name = os.path.basename(path)            

            cherrypy.response.headers["Content-Type"] = content_type
            cherrypy.response.headers["Content-Disposition"] = \
                "%s; filename=%s" % (disposition, name)

            try:
                handler(path, content_type)
            except CantHandleFile:
                pass
            else:
                return cherrypy.response.body

    return cp_serve_file(path, content_type, disposition, name)


class CantHandleFile(Exception):
    """An exception raised by a MIME type file handler to indicate it cedes
    control back to the default static file publisher.
    """

