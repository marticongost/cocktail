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
    from cocktail.cache import Cache
    from cocktail.controllers.static import handles_content_type

    add_type("text/switchcss", ".sss")

    class SSSCache(Cache):

        def load(self, key):
            return SSSStyleSheet(key).cssText

        def _is_current(self, entry):
            
            if not Cache._is_current(self, entry):
                return False

            # Reprocess modified files
            # TODO: take 'include' directives into account, recursively
            # Sadly, Switch doesn't seem to expose this information
            try:
                mtime = os.stat(entry.key).st_mtime
            except:
                return False
            else:
                return entry.creation >= mtime

    cache = SSSCache()

    @handles_content_type("text/switchcss")
    def switch_css_handler(path, content_type):

        try:    
            css = cache.request(path)
        except:
            raise cherrypy.NotFound()

        cherrypy.response.headers["Content-Type"] = "text/css"
        cherrypy.response.headers["Last-Modified"] = \
            http.HTTPDate(cache[path].creation)
        cptools.validate_since()
        cherrypy.response.body = [css]

