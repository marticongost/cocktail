#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from .controller import Controller

http_methods = (
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH"
)


class HTTPMethodController(Controller):

    def resolve(self, path):

        method = cherrypy.request.method
        impl = self.get_http_method_implementation(method)

        if impl is None:
            raise cherrypy.HTTPError(405)

        return impl

    def get_http_method_implementation(self, method):
        impl = getattr(self, method, None)
        return None if not getattr(impl, "exposed", False) else impl

    @cherrypy.expose
    def OPTIONS(self, **kwargs):
        cherrypy.response.headers["Allow"] = ", ".join(
            method
            for method in http_methods
            if self.get_http_method_implementation(method)
        )

