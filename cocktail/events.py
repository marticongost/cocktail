#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from weakref import ref, WeakKeyDictionary
from cocktail.modeling import SynchronizedList
from threading import Lock


def when(event):
    def decorator(function):
        event.append(function)
        return function

    return decorator


class Event(object):

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
            slot.target = ref(target)
            self.__slots[target] = slot

            if is_instance:
                slot.next = self.__get_slot(target.__class__),
            else:
                slot.next = map(self.__get_slot, target.__bases__)

        return slot


class EventSlot(SynchronizedList):

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

    target = None
    source = None
    slot = None
    consumed = False
    
    def __init__(self, params):
        for key, value in params.iteritems():
            setattr(self, key, value)


