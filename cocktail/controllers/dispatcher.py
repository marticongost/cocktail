#-*- coding: utf-8 -*-
u"""

@author:		Martí­ Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from inspect import isfunction, getargspec
import cherrypy
from cocktail.modeling import getter, ListWrapper, ContextualDict
from cocktail.controllers.requesthandler import RequestHandler

context = ContextualDict()


class HandlerActivator(object):

    def __init__(self, callable, *args, **kwargs):
        self.callable = callable
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):

        request = cherrypy.request
        request_error = None
        visited = []
        context["visited_handlers"] = visited

        try:
            try:
                # Descend from the root to the final handler
                parent = None

                for handler in request.handler_chain:

                    context["parent_handler"] = parent
                    visited.append(handler)

                    # Trigger the 'before_request' event on those handlers that
                    # support it
                    event_slot = getattr(handler, "before_request", None)
                    if event_slot is not None:
                        event_slot()

                    parent = handler
                    
                # Execute the response handler
                try:                    
                    return self.callable(*self.args, **self.kwargs)

                except TypeError, x:

                    callable = self.callable
                    
                    if not isfunction(callable):
                        callable = getattr(callable, "im_func", callable)
                        if not isfunction(callable) \
                        and hasattr(callable, "__call__"):
                            callable = callable.__call__.im_func
                    
                    if callable:                        
                        (args, varargs, varkw, defaults) = getargspec(callable)

                        if args and args[0] == "self":
                            args = args[1:]
                        
                        if len(self.args) < len(args) \
                        or (len(self.args) > len(args) and not varargs):
                            raise cherrypy.NotFound()

                    raise
            
            except cherrypy.HTTPRedirect: 
                raise

            except StopRequest:
                raise

            # Custom error handlers
            except Exception, request_error:
                for handler in reversed(visited):
                    event_slot = getattr(handler, "exception_raised", None)
                    if event_slot is not None:
                        event_info = event_slot(
                            exception = request_error,
                            handled = False
                        )
                        if event_info.handled:
                            break
                else:
                    raise       

            # Cleanup
            finally:
                flow_control_errors = (
                    cherrypy.HTTPError,
                    cherrypy.HTTPRedirect,
                    StopRequest
                )
                flow_exception = None
                
                for handler in reversed(visited):
                    event_slot = getattr(handler, "after_request", None)
                    if event_slot is not None:
                        try:
                            event_slot(
                                flow_exception = flow_exception,
                                error = request_error
                            )
                        except flow_control_errors, exception:
                            if exception is not None:
                                flow_exception = exception

                if flow_exception:
                    raise flow_exception

        except StopRequest:
            pass
    
        return cherrypy.response.body

    def _get_kwargs(self):
        kwargs = cherrypy.request.params.copy()
        if self._kwargs:
            kwargs.update(self._kwargs)
        return kwargs
    
    def _set_kwargs(self, kwargs):
        self._kwargs = kwargs
    
    kwargs = property(_get_kwargs, _set_kwargs)


class Dispatcher(object):

    def __call__(self, path_info, handler = None):

        request = cherrypy.request

        # Configuration
        config = getattr(request, "config", None)

        if config is None:
            config = cherrypy.config.copy()
            request.config = config
        
        # Path components
        if isinstance(path_info, basestring):
            parts = self.split(path_info)
        else:
            parts = list(path_info)

        path = self.__class__.PathProcessor(parts)

        # Handler chain
        if handler is None:
            handler = request.app.root

        parent = None
        
        chain = getattr(request, "handler_chain", None)

        if chain is None:
            chain = []
            request.handler_chain = chain
            context.clear()

        # Traverse handlers
        try:

            while True:

                # Instantiate classes
                if isinstance(handler, type):
                    handler = handler()
                
                if not getattr(handler, "exposed", False):
                    handler = None
                    break

                # Add the handler to the execution chain
                chain.append(handler)

                # Handler specific configuration
                handler_config = getattr(handler, "_cp_config", None)
                
                if handler_config is not None:
                    config.update(handler_config)

                # Path specific configuration (overrides per-handler configuration)
                path_config = request.app.config.get(path.current_path)

                if path_config:
                    config.update(path_config)

                # Trigger the 'traversed' event
                event_slot = getattr(handler, "traversed", None)
                if event_slot is not None:
                    event_slot(path = path, config = config)

                # Descend:                
                child = None

                # Named child
                if path:
                    child_name = path[0]
                    if not child_name[0] == "_":
                        child = getattr(handler, child_name, None)
                        if child:
                            if getattr(child, "exposed", False):
                                path.pop(0)
                            else:
                                child = None

                # Dynamic resolver
                if child is None:
                    resolver = getattr(handler, "resolve", None)
                    if resolver:
                        child = resolver(path)

                # End of the road: no child could be retrieved, or the handler
                # resolves to itself
                if child is None or child is handler: 
                    break
                else:
                    handler = child
        
        except Exception, error:
            def handler(*args, **kwargs):
                raise error
            chain.append(handler)
        
        request.handler = HandlerActivator(handler, *path)
    
    def respond(self, path_info, handler = None):
        self(path_info, handler)
        return cherrypy.request.handler()

    def split(self, path):
        return [self.normalize_component(component)
                for component in path.strip('/').split('/')
                if component]

    def normalize_component(self, component):
        return component.replace("%2F", "/")
       
    class PathProcessor(ListWrapper):

        def __init__(self, path):
            ListWrapper.__init__(self, path)
            self.__consumed_components = []

        def pop(self, index = -1):

            if index < 0:
                index = len(self._items) + index

            component = self._items.pop(index)
            
            if index == 0:
                self.__consumed_components.append(component)

            return component
            
        @getter
        def current_path(self):
            return "/" + "/".join(component
                                  for component in self.__consumed_components)


class StopRequest(Exception):
    """An exception raised to stop the processing of the current request
    without triggering an error. When raised by a request handler, the
    exception will be caught and silenced by the dispatcher."""


if __name__ == "__main__":
    
    class TestController(object):

        @cherrypy.expose
        def index(self, foo = None):
            prev_foo = getattr(cherrypy.request, "foo", "None")
            cherrypy.request.foo = foo
            return prev_foo

    cherrypy.quickstart(TestController, "/", {
        "global": {
            "request.dispatch": Dispatcher()
        }
    })

