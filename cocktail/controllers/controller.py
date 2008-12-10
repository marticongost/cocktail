#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
import buffet
from cocktail.modeling import ListWrapper
from cocktail.html import templates
from cocktail.events import EventHub, Event
from cocktail.controllers.requestproperty import request_property
from cocktail.controllers.dispatcher import StopRequest
from cocktail.controllers.parameters import FormSchemaReader

_rendering_engines = {}


class Controller(object):
    
    __metaclass__ = EventHub
    
    # Default configuration
    #------------------------------------------------------------------------------    
    _cp_config = {
        "rendering.engine": "cocktail",
        "rendering.format": "html"
    }

    # Execution and lifecycle
    #------------------------------------------------------------------------------    
    exposed = True

    def __call__(self):
        try:
            if self.ready:
                self.submit()
                self.successful = True
        except self.handled_errors, ex:
            self.output["error"] = ex
        
        return self.render()
    
    def submit(self):
        pass

    @request_property
    def submitted(self):
        return True

    @request_property
    def valid(self):
        return True

    @request_property
    def ready(self):
        return self.submitted and self.valid

    @request_property
    def successful(self):
        pass

    traversed = Event(doc = """
        An event triggered when the
        L{dispatcher<cocktail.controllers.dispatcher.Dispatcher>} passes
        through or reaches the controller while looking for a request handler.

        @ivar path: A list-like object containing the remaining path components
            that haven't been consumed by the dispatcher yet.
        @type path: L{PathProcessor
                      <cocktail.controllers.dispatcher.PathProcessor>}

        @ivar config: The configuration dictionary with all entries that apply
            to the controller. Note that this dictionary can change as the
            dispatcher traverses through the handler hierarchy. Event handlers
            are free to modify it to change configuration as required.
        @type config: dict
        """)

    before_request = Event(doc = """
        An event triggered before the controller (or one of its nested
        handlers) has been executed.
        """)

    after_request = Event(doc = """
        An event triggered after the controller (or one of its nested handlers)
        has been executed. This is guaranteed to run, regardless of errors.
        """)

    # Error handling
    #------------------------------------------------------------------------------    
    handled_errors = ()

    exception_raised = Event(doc = """
        An event triggered when an exception is raised by the controller or one
        of its descendants. The event is propagated up through the handler
        chain, until it reaches the top or it is stoped by setting its
        L{handled} attribute to True.

        @param exception: The exception being reported.
        @type exception: L{Exception}

        @param handled: A boolean indicating if the exception has been dealt
            with. Setting this to True will stop the propagation of the event
            up the handler chain, while a False value will cause the exception
            to continue to be bubbled up towards the application root and,
            eventually, the user.
        @type handled: bool
        """)

    # Input / Output
    #------------------------------------------------------------------------------
    @request_property
    def params(self):
        return FormSchemaReader()

    @request_property
    def output(self):
        return {}
    
    # Rendering
    #------------------------------------------------------------------------------   
    rendering_format_param = "format"
    allowed_rendering_formats = frozenset(["html", "xhtml", "json"])

    @request_property
    def rendering_format(self):

        format = None

        if self.rendering_format_param:
            format = cherrypy.request.params.get(self.rendering_format_param)
            
        if format is None:
            format = cherrypy.request.config["rendering.format"]

        return format

    @request_property
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

    @request_property
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
        return dumps(self.output)

