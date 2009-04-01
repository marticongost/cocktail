#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from cocktail.events import Event, EventHub


class RequestHandler(object):
    
    __metaclass__ = EventHub

    exposed = True

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


class handler(RequestHandler):

    def __init__(self, func):
        self.__call__ = func

