#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from copy import copy

class EventLog(list):

    def listen(self, *args, **kwargs):
        for slot in args:
            self._add_listener(slot)

        for name, slot in kwargs.iteritems():
            self._add_listener(slot, name)

    def _add_listener(self, slot, name = None):

        def listener(event):
            self.append(copy(event))

        if name:
            listener.func_name = name

        slot.append(listener)

    def clear(self):
        while self:
            self.pop(0)

def run_concurrently(thread_count, func, *args, **kwargs):

    from thread import start_new_thread
    from threading import Condition

    condition = Condition()

    # Dummy class to work around python's scoping limitations
    class ExecutionContext(object):
        error = None
        finished_threads = 0

    def thread_runner():
        try:
            func(*args, **kwargs)
        except Exception, error:
            ExecutionContext.error = error

        condition.acquire()
        ExecutionContext.finished_threads += 1
        condition.notify()
        condition.release()

    for i in range(thread_count):
        if ExecutionContext.error is not None:
            break
        
        start_new_thread(thread_runner, ())

    try:
        condition.acquire()
        while ExecutionContext.finished_threads < thread_count \
        and ExecutionContext.error is None:
            condition.wait()
    finally:
        condition.release()

    if ExecutionContext.error:
        raise ExecutionContext.error

