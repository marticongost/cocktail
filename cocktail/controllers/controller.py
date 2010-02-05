#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from warnings import warn
import cherrypy
from simplejson import dumps
from cocktail.modeling import ListWrapper, cached_getter
from cocktail.events import Event
from cocktail.controllers.dispatcher import StopRequest, context
from cocktail.controllers.parameters import FormSchemaReader
from cocktail.controllers.requesthandler import RequestHandler
from cocktail.controllers.renderingengines import get_rendering_engine


class Controller(RequestHandler):
 
    context = context
    
    # Default configuration
    #------------------------------------------------------------------------------    
    default_rendering_engine = "cocktail"
    default_rendering_format = "html"

    # Execution and lifecycle
    #------------------------------------------------------------------------------    
    exposed = True

    def __call__(self, **kwargs):
        try:
            if self.ready:
                self.submit()
                self.successful = True
            self.processed()
        except Exception, ex:
            self.handle_error(ex)
        
        return self.render()
    
    def submit(self):
        pass

    @cached_getter
    def submitted(self):
        return True

    @cached_getter
    def valid(self):
        return True

    @cached_getter
    def ready(self):
        return self.submitted and self.valid

    successful = False
    
    handled_errors = ()

    def handle_error(self, error):
        if isinstance(error, self.handled_errors):
            self.output["error"] = error
        else:
            raise

    processed = Event(doc = """
        An event triggered after the controller's logic has been invoked.        
        """)

    # Input / Output
    #------------------------------------------------------------------------------
    @cached_getter
    def params(self):
        return FormSchemaReader()

    @cached_getter
    def output(self):
        return {}
    
    # Rendering
    #------------------------------------------------------------------------------   
    rendering_format_param = "format"
    allowed_rendering_formats = frozenset(["html", "xhtml", "json"])

    def _get_rendering_engine(self, engine_name):
        warn(
            "Controller._get_rendering_engine() is deprecated, use "
            "cocktail.controllers.renderingengines.get_rendering_engine() instead",
            DeprecationWarning,
            stacklevel = 2
        )
        return get_rendering_engine(engine_name)

    @cached_getter
    def rendering_format(self):

        format = None

        if self.rendering_format_param:
            format = cherrypy.request.params.get(self.rendering_format_param)
            
        if format is None:
            format = cherrypy.request.config.get(
                "rendering.format",
                self.default_rendering_format
            )

        return format

    @cached_getter
    def rendering_engine(self):
        engine_name = cherrypy.request.config.get(
            "rendering.engine",
            self.default_rendering_engine
        )
        return get_rendering_engine(engine_name)

    @cached_getter
    def view_class(self):
        return None

    def render(self):

        format = self.rendering_format
       
        if format and format in self.allowed_rendering_formats:
            renderer = getattr(self, "render_" + format, None)
        else:
            renderer = None
        
        if renderer is None:
            raise ValueError(
                "%s can't render its response in '%s' format" % (self, format))

        return renderer()
           
    def _render_template(self):

        view_class = self.view_class

        if view_class:
            output = self.output
            output["submitted"] = self.submitted
            output["successful"] = self.successful
            return self.rendering_engine.render(
                            output,
                            format = self.rendering_format,
                            template = view_class)
        else:
            return ""

    def render_html(self):
        return self._render_template()

    def render_xhtml(self):
        return self._render_template()

    def render_json(self):
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return dumps(self.output)

    @classmethod
    def copy_config(cls, **kwargs):
        config = getattr(cls, "_cp_config", None)
        config = {} if config is None else config.copy
        config.update(kwargs)
        return config

