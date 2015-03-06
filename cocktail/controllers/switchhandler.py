#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
try:
    from switch.StyleSheet import SSSStyleSheet
except ImportError:
    pass
else:
    import os
    from mimetypes import add_type
    import cherrypy
    from cherrypy.lib import cptools, http
    from cocktail.resourceloader import ResourceLoader
    from cocktail.controllers.static import handles_content_type

    add_type("text/switchcss", ".sss")

    class SSSLoader(ResourceLoader):

        def load(self, key):
            return SSSStyleSheet(key)

        def _is_current(self, resource, invalidation = None, verbose = False):

            if not ResourceLoader._is_current(
                self, resource, invalidation = invalidation, verbose = verbose
            ):
                return False

            # Reprocess modified files
            try:
                return resource.creation >= resource.value.get_last_update()
            except OSError, IOError:
                return False

    cache = SSSLoader()

    @handles_content_type("text/switchcss")
    def switch_css_handler(path, content_type):

        try:
            stylesheet = cache.request(path)
        except OSError, IOError:
            raise cherrypy.NotFound()

        cherrypy.response.headers["Content-Type"] = "text/css"
        cherrypy.response.headers["Last-Modified"] = \
            http.HTTPDate(cache[path].creation)
        cptools.validate_since()
        cherrypy.response.body = [stylesheet.cssText]

