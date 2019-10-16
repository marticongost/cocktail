"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any, Callable, Iterable, Mapping, Tuple, Type
from types import MethodType
from weakref import ref, WeakKeyDictionary
from cocktail.modeling import SynchronizedList
from threading import Lock, current_thread
from contextlib import contextmanager

EventHandler = Callable[["EventInfo"], Any]


def when(event: "EventSlot") -> Callable[[EventHandler], EventHandler]:
    """A decorator factory that attaches decorated functions as event handlers
    for the given event slot.

    :param event: The event slot to register the decorated function on.

    :return: The decorator that does the binding.
    """
    def decorator(function):
        event.append(function)
        return function

    return decorator


class event_handler:
    """A decorator that simplifies defining class level event handlers."""

    prefix = "handle_"

    def __init__(self, func):
        self.__func__ = func

    def __get__(self, instance, type=None):
        if instance:
            return self.__func__
        else:
            return self

    def __set_name__(self, owner, name):

        if not name.startswith(self.prefix):
            raise ValueError(
                f"Event handler {name} at {owner} should have a name starting "
                f"with {self.prefix}"
            )

        event_name = name[len(self.prefix):]
        event_slot = getattr(owner, event_name, None)

        if event_slot is None or not isinstance(event_slot, EventSlot):
            raise TypeError(
                f"Can't attach {name}() at {owner} to the {event_name} event, "
                "the indicated event doesn't exist"
            )

        event_slot.append(self.__func__)


class Event:
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

    def __init__(
            self,
            doc: str = None,
            event_info_class: Type["EventInfo"] = None):
        """Declares a new event.

        @param doc: The docstring for the event.
        @param event_info_class: If given, invoking this event will use
            instances of the given subclass of `EventInfo` in order to describe
            their context. If not set, `EventInfo` will be used by default.
        """
        self.__doc__ = doc
        self.__slots = WeakKeyDictionary()
        self.__lock = Lock()
        self.event_info_class = event_info_class or EventInfo

    def __get__(self, instance, type=None):

        self.__lock.acquire()

        try:
            if instance is None:
                return self.__get_slot(type)
            else:
                return self.__get_slot(instance, True)
        finally:
            self.__lock.release()

    def __get_slot(self, target, is_instance=False):

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
                slot.next = list(map(self.__get_slot, target.__bases__))

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

    def __call__(
            self,
            _event_info: "EventInfo" = None,
            **kwargs) -> "EventInfo":

        target = self.target()

        # self.target is a weakref, so the object may have expired
        if target is None:
            return

        if _event_info is None:
            event_info = self.event.event_info_class(kwargs)
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

    def append(self, callback: EventHandler):
        """Registers an event handler as the last entry in the slot.

        :param callback: The handler to append.
        """
        SynchronizedList.append(self, self.wrap_callback(callback))

    def insert(self, position: int, callback: EventHandler):
        """Inserts an event handler as the given ordinal position of the slot.

        :param position: The index to place the handler at.
        :param callback: The handler to append.
        """
        SynchronizedList.insert(self, position, self.wrap_callback(callback))

    def __setitem__(self, position: int, callback: EventHandler):
        """Replaces the event handler at the given index with a new event
        handler.

        :param position: The index to replace.
        :param callback: The handler to append.
        """
        SynchronizedList.__setitem__(
            self,
            position,
            self.wrap_callback(callback)
        )

    def extend(self, callback_sequence: Iterable[EventHandler]):
        """Extends all the event handlers in the given sequence at the end of
        the slot.

        :param callback_sequence: The iterable sequence of event handlers to
            add to the slot.
        """
        SynchronizedList.extend(
            self,
            (self.wrap_callback(callback) for callback in callback_sequence)
        )

    def wrap_callback(self, callback: EventHandler):

        # Transform methods bound to the target for the event slot into a
        # callable that achieves the same effect without maintining a hard
        # reference to the target object, which would keep the target object
        # alive undefinitely
        if isinstance(callback, MethodType) \
        and callback.__self__ is self.target() \
        and not isinstance(callback.__self__, type):
            callback = BoundCallback(callback.__func__)

        return callback


class BoundCallback:

    def __init__(self, func):
        self._func = func

    def __call__(self, event: "EventInfo") -> Any:
        return self._func(event.source, event)

    def __eq__(self, other: Any) -> bool:
        return type(self) is type(other) and self._func is other._func


class EventInfo:
    """An object that encapsulates all the information passed on to event
    handlers when an `event slot <EventSlot>` is triggered.

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
    target: Any = None
    source: Any = None
    slot: EventSlot = None
    consumed: bool = False

    def __init__(self, params: Mapping[str, Any]):
        for key, value in params.items():
            setattr(self, key, value)

    @property
    def event(self) -> Event:
        return self.slot.event


@contextmanager
def monitor_thread_events(
        *monitoring: Iterable[Tuple[EventSlot, EventHandler]]):
    """A context manager that installs temporary event handlers for the current
    thread.

    The context manager receives a sequence of slot, handler tuples. Within its
    context, whenever the given slots are triggered their matching event
    handlers will be invoked, but only if they are triggered from the current
    thread. All the registered handlers are guaranteed to be removed when the
    context finishes.

    :param monitoring: An iterable sequence of slot, event handler pairs.
    """

    handlers = []

    for slot, callback in monitoring:
        handler = _PerThreadHandler(callback)
        handlers.append((slot, handler))
        slot.append(handler)

    try:
        yield None
    finally:
        for slot, handler in handlers:
            try:
                slot.remove(handler)
            except ValueError:
                pass


class _PerThreadHandler(object):

    def __init__(self, callback):
        self.owner_thread_id = current_thread().ident
        self.callback = callback

    def __call__(self, e):
        if current_thread().ident == self.owner_thread_id:
            return self.callback(e)

