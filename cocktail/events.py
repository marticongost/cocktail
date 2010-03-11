#-*- coding: utf-8 -*-
"""
An event mechanism for python.
"""
from weakref import ref, WeakKeyDictionary
from cocktail.modeling import SynchronizedList
from threading import Lock


def when(event):
    """A decorator factory that attaches decorated functions as event handlers
    for the given event slot.
    
    :param event: The event slot to register the decorated function on.
    :type event: `EventSlot`

    :return: The decorator that does the binding.
    :rtype: callable
    """
    def decorator(function):
        event.append(function)
        return function

    return decorator


class EventHub(type):
    """A convenience metaclass that automatically registers methods marked with
    the `event_handler` decorator as class-level event-handlers. 
    """

    def __init__(cls, name, bases, members):
        type.__init__(cls, name, bases, members)

        for key, member in members.iteritems():
            
            if isinstance(member, event_handler):
                handler = getattr(cls, key)
                event_name = key[7:]
                event_slot = getattr(cls, event_name, None)

                if event_slot is None or not isinstance(event_slot, EventSlot):
                    raise TypeError(
                        "Can't attach %s to the %s event on %s, "
                        "indicated event doesn't exist"
                        % (member, event_name, cls)
                    )

                event_slot.append(handler)


class event_handler(classmethod):
    """A decorator that works hand in hand with `EventHub` in order to ease
    the attachment of handlers to events.
    """


class Event(object):
    """An event describes a certain condition that can be triggered on a class
    and/or its instances. Users of the class can register callback functions
    that will be invoked when the event is triggered, which results in a
    flexible extensibility mechanism.

    This class is a descriptor, and does nothing but produce and cache
    `event slots <EventSlot>` on the class, its subclasses or its instances, in
    a thread-safe manner. Each object that the event is requested on spawns a
    new slot, which will remain assigned to that object throughout the object's
    life cycle.
    """

    def __init__(self, doc = None):
        self.__doc__ = doc
        self.__slots = WeakKeyDictionary()
        self.__lock = Lock()

    def __get__(self, instance, type = None):
        
        self.__lock.acquire()
                
        try:
            if instance is None:
                return self.__get_slot(type)
            else:
                return self.__get_slot(instance, True)
        finally:
            self.__lock.release()

    def __get_slot(self, target, is_instance = False):

        slot = self.__slots.get(target)

        if slot is None:
            slot = EventSlot()
            slot.__doc__ = self.__doc__
            slot.event = self
            slot.target = ref(target)
            self.__slots[target] = slot

            if is_instance:
                slot.next = self.__get_slot(target.__class__),
            else:
                slot.next = map(self.__get_slot, target.__bases__)

        return slot


class EventSlot(SynchronizedList):
    """A binding between an `Event` and one of its targets.
    
    Slots work as callable lists of callbacks. They possess all the usual list
    methods, plus the capability of being called. When the slot is called,
    callbacks in the slot are executed in order, and keyword parameters are
    forwarded to these callbacks, wrapped in an instance of the `EventInfo`
    class.

    .. attribute:: event
    
        The `event <Event>` that the slot stores responses for.

    .. attribute:: target

        The object that the slot is bound to.
    
    .. attribute:: next

        A list of other event slots that will be chained up to the slot. After
        a slot has been triggered, and its callbacks processed, its chained
        slots will also be triggered. This is done recursively. For example,
        this is used to trigger class-wide events after activating an instance
        slot.
    """
    event = None
    target = None
    next = ()

    def __call__(self, _event_info = None, **kwargs):
        
        target = self.target()

        # self.target is a weakref, so the object may have expired
        if target is None:
            return
       
        if _event_info is None:
            event_info = EventInfo(kwargs)
            event_info.source = target
        else:
            event_info = _event_info

        event_info.slot = self
        event_info.target = target
        event_info.consumed = False
        
        for callback in self:
            callback(event_info)

            if event_info.consumed:
                break

        for next_slot in self.next:
            next_slot(_event_info = event_info)

        return event_info


class EventInfo(object):
    """An object that encapsulates all the information passed on to callbacks
    when an `event slot <EventSlot>` is triggered.

    .. attribute:: target
        
        The object that the event is being triggered on.
    
    .. attribute:: source
        
        The object that the event originated in. While the `target` attribute
        can change as the event `propagates between slots <EventSlot.next>`,        
        `source` will always point to the first element on which the event was
        invoked.

    .. attribute:: slot

        The `event slot <EventSlot>` from which the callback is being
        triggered.

    .. attribute:: consumed

        If a callback sets this flag to True, no further callbacks will be
        invoked for this event.
    """    
    target = None
    source = None
    slot = None
    consumed = False
    
    def __init__(self, params):
        for key, value in params.iteritems():
            setattr(self, key, value)

