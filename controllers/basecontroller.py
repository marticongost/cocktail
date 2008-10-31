#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from cocktail.modeling import ListWrapper, getter, cached_getter
from cocktail.html import templates
from cocktail.controllers.parameters import FormSchemaReader
from cocktail.controllers.location import Location, HTTPPostRedirect


class BaseController(object):
    
    view_class = None
    success_view_class = None
    success_redirection = None
    handled_errors = ()

    def __init__(self):
        self.successful = False
        self.error = None

    @cherrypy.expose
    def index(self, *args, **kwargs):

        try:
            self.begin()

            if self.is_ready():
                self.submit(*args, **kwargs)
                self.successful = True
                
                redirection = self.success_redirection

                if redirection is not None:
                    if isinstance(redirection, Location):
                        redirection.go()
                    else:
                        raise cherrypy.HTTPRedirect(redirection)

        except Exception, error:

            self.error = error

            if isinstance(error, HTTPPostRedirect):
                return cherrypy.response.body
            elif not isinstance(error, self.handled_errors):
                raise

        finally:
            self.end()
        
        return self.view.render_page()

    @getter
    def redirecting(self):
        return self.error and isinstance(
            self.error,
            (cherrypy.HTTPRedirect, HTTPPostRedirect)
        )

    def begin(self):
        pass

    def is_ready(self):
        return False

    def submit(self):
        pass

    def end(self):
        pass

    @cached_getter
    def params(self):
        reader = FormSchemaReader()
        self._init_form_reader(reader)
        return reader

    def _init_form_reader(self, reader):
        pass

    @cached_getter
    def view(self):
        view = self._create_view()
        self._init_view(view)
        return view

    def _create_view(self):

        view_class = self.successful and self.success_view_class \
            or self.view_class

        return templates.new(view_class)

    def _init_view(self, view):
        view.error = self.error
        view.successful = self.successful

