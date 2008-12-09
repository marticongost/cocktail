#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from cocktail.modeling import ListWrapper, abstract_method
from cocktail.html import templates
from cocktail.events import EventHub, Event
from cocktail.controllers.requestproperty import request_property
from cocktail.controllers.dispatcher import StopRequest
from cocktail.controllers.parameters import FormSchemaReader


class Controller(object):
    
    __metaclass__ = EventHub
    
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
        except:
            raise

        return self.render()
    
    @abstract_method
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

        @ivar chain: The chain of parent handlers for the controller, from the
            root to the handler itself (both included).

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

    starting = Event(doc = """
        An event triggered before invoking the handler logic.
        """)

    ending = Event(doc = """
        An event triggered after invoking the handler logic.
        """)

    # Error handling
    #------------------------------------------------------------------------------    
    handled_errors = ()

    exception_raised = Event(doc """
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
    def reader(self):
        return FormSchemaReader()

    @request_property
    def input_schema(self):
        return None

    @request_property
    def input(self):
        schema = self.input_schema
        if schema:
            return self.reader.read(schema)
        else:
            return {}

    @request_property
    def output(self):
        return {}
    
    # Rendering
    #------------------------------------------------------------------------------    
    @request_property
    def format(self):
        return cherrypy.params.get("format", self.default_format)
    
    @request_property
    def default_format(self):
        return "html"

    @request_property
    @abstract_method
    def view_class(self):
        pass

    @request_property
    def view(self):
        
        view = None
        view_class = self.view_class

        if view_class:
            if isinstance(view_class, basestring):
                view = templates.new(view_class)
            else:
                view = view_class()

            for key, value in self.output.iteritems():
                setattr(view, key, value)
            
        return view

    def render(self):
        format = self.format
        renderer = getattr(self, "render_" + format, None)
        
        if renderer is None:
            raise ValueError(
                "%s can't render its response in '%s' format" % (self, format))

        return renderer()

    def render_html(self):
        view = self.view
        
        view.submitted = self.submitted:
        view.successful = self.successful
        
        if view:
            return view.render_page()

    def render_json(self):
        return dumps(self.output)

