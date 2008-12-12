#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
import buffet
from simplejson import dumps
from cocktail.modeling import ListWrapper, cached_getter
from cocktail.html import templates
from cocktail.controllers.dispatcher import StopRequest, context
from cocktail.controllers.parameters import FormSchemaReader
from cocktail.controllers.requesthandler import RequestHandler

_rendering_engines = {}


class Controller(RequestHandler):
 
    context = context
    
    # Default configuration
    #------------------------------------------------------------------------------    
    _cp_config = {
        "rendering.engine": "cocktail",
        "rendering.format": "html"
    }

    # Execution and lifecycle
    #------------------------------------------------------------------------------    
    exposed = True

    def __call__(self, **kwargs):
        try:
            if self.ready:
                self.submit()
                self.successful = True
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

    @cached_getter
    def rendering_format(self):

        format = None

        if self.rendering_format_param:
            format = cherrypy.request.params.get(self.rendering_format_param)
            
        if format is None:
            format = cherrypy.request.config["rendering.format"]

        return format

    @cached_getter
    def rendering_engine(self):
        engine_name = cherrypy.request.config["rendering.engine"]
        return self._get_rendering_engine(engine_name)
        
    def _get_rendering_engine(self, engine_name):

        engine = _rendering_engines.get(engine_name)

        if engine is None:
            engine_type = buffet.available_engines[engine_name]
            engine = engine_type()
            _rendering_engines[engine_name] = engine

        return engine

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
                            self.output,
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

