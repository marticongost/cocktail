#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from __future__ import with_statement
from types import GeneratorType
from time import time
from threading import RLock, Thread
from cocktail.modeling import getter, DictWrapper


class TaskManager(DictWrapper):

    expiration = None

    def __init__(self):
        DictWrapper.__init__(self)
        self.__id = 0
        self.__lock = RLock()

    def task(self, func, callback = None, id = None):

        with self.__lock:

            if id is None:
                id = self.__id + 1
                while id in self._items:
                    id += 1
                self.__id = id
            else:
                task = self._items.get(id)
                if task:
                    return task

            task = Task(id, func, callback)
            self._items[task.id] = task

        task.start()
        return task

    def remove_task(self, task):
        with self.__lock:
            del self._items[task.id]

    def remove_expired_tasks(self):
        with self.__lock:
            now = time()
            for task in self.values():
                if task.completed and task.end_time - now > self.expiration:
                    self.remove_task(task)


class Task(Thread):

    state = None

    def __init__(self, id, func, callback = None):
        Thread.__init__(self)
        self.__id = id
        self.__func = func
        self.__callback = callback
        self.__end_time = None

    @getter
    def id(self):
        return self.__id

    @getter
    def completed(self):
        return self.__end_time is not None

    @getter
    def end_time(self):
        return self.__end_time

    def run(self):

        rvalue = self.__func()

        if isinstance(rvalue, GeneratorType):
            for state in self.__func():
                self.state = state
                if self.__callback:
                    self.__callback(self)

        else:
            self.state = rvalue

        self.__end_time = time()

        if self.__callback:
            self.__callback(self)

