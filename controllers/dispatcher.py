#-*- coding: utf-8 -*-
"""

@author:		MartÃ­ Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
import cherrypy
from cocktail.modeling import getter, ListWrapper

BasePageHandler = cherrypy._cpdispatch.LateParamPageHandler


class PageHandler(BasePageHandler):
    
    handler_chain = None

    def __call__(self, *args, **kwargs):
        try:
            return BasePageHandler.__call__(self, *args, **kwargs)
        except cherrypy.HTTPRedirect:
            raise
        except StopRequest:
            return cherrypy.request.body
        except Exception, ex:
            for handler in reversed(self.handler_chain):
                event_slot = getattr(handler, "exception_raised", None)

                if event_slot is not None:
                    event_info = event_slot(exception = ex, handled = False)
                    if event_info.handled:
                        break
            else:
                raise


class Dispatcher(object):

    def __call__(self, path_info, handler = None):

        request = cherrypy.request
        path = self.__class__.PathProcessor(self.split(path_info))
        config = {}
        is_default = False

        if handler is None:
            handler = request.app.root

        chain = []
        handler = self.resolve_handler(handler, chain, path, config)
        
        while handler and path:

            child = getattr(handler, path[0], None)

            # Named child
            if child:
                path.pop(0)
                child = self.resolve_handler(child, chain, path, config)

            # Dynamic resolver
            else:
                resolver = getattr(handler, "resolve", None)

                if resolver:
                    child = resolver(path)

                    if child:
                        child = self.resolve_handler(
                                    child, chain, path, config)
            
            # Generic method with positional parameters
            if child is None:
                child = getattr(handler, "default", None)
                
                if child is not None:
                    child = self.resolve_handler(child, chain, path, config)
                    is_default = True

            handler = child

            if is_default:
                request.is_index = not path
                break

        # Extra path components are only supported on the default method
        if path and not is_default:
            handler = None

        # Resolve 'index' handlers, recursively
        if handler is not None and not callable(handler):
            request.is_index = True
            while handler is not None and not callable(handler):
                child = getattr(handler, "index", None)
                if child is None:
                    handler = None
                else:
                    handler = \
                        self.resolve_handler(child, chain, path, config)
        
        request.config = config

        if handler is not None and getattr(handler, "exposed", False):
            request.handler = cherrypy._cpdispatch.PageHandler(handler, *path)
            request.handler.handler_chain = chain
        else:
            request.handler = cherrypy.NotFound()

    def split(self, path):
        return [self.normalize_component(component)
                for component in path.strip('/').split('/')
                if component]

    def normalize_component(self, component):
        return component.replace("%2F", "/")
       
    def resolve_handler(self, handler, chain, path, config):
        
        # Add the handler to the execution chain
        chain.append(handler)

        # Instantiate classes
        if isinstance(handler, type):
            handler = handler()
            handler.parent = parent

        # Handler specific configuration
        handler_config = getattr(handler, "_cp_config", None)
        
        if handler_config is not None:
            config.update(handler_config)

        # Path specific configuration (overrides per-handler configuration)
        path_config = cherrypy.request.app.config.get(path.current_path)

        if path_config:
            config.update(path_config)

        # Trigger the 'traversed' event on those handlers that support it
        traversed_event = getattr(handler, "traversed", None)

        if traversed_event is not None:
            traversed_event(chain = chain, path = path, config = config)       

        return handler

    class PathProcessor(ListWrapper):

        def __init__(self, path):
            ListWrapper.__init__(self, path)
            self.__consumed_components = []

        def pop(self, index):
            component = self._items.pop(index)
            self.__consumed_components.append(component)
            
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

