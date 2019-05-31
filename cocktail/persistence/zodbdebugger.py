#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import defaultdict
try:
    from collections import Counter
except ImportError:
    from backport_collections import Counter

from threading import local
from contextlib import contextmanager
import traceback
from ZODB.Connection import Connection
from cocktail.styled import styled

_thread_data = local()

class ZODBDebugger(object):

    def __init__(self, action = "count", filter = None):
        self.action = action
        self.filter = filter
        self.count = Counter()
        self.blame = defaultdict(Counter)

    def begin(self):
        self.count.clear()
        _thread_data.debugger = self

    def end(self):
        _thread_data.debugger = None

    def __enter__(self):
        self.begin()

    def __exit__(self, type, value, traceback):
        self.end()
        if self.action == "count":
            self.show_count()
        elif self.action == "blame":
            self.show_blame()

    def show_count(self):
        for cls, count in self.count.most_common():
            print styled(cls, "slate_blue"), count

    def show_blame(self):
        for cls, tb_count in self.blame.iteritems():
            print styled(cls, "slate_blue")
            for tb, count in tb_count.most_common():
                print
                print "%s reads" % styled(count, style = "bold")
                for fname, line, func, code in tb:
                    print "  %s %s:%d" % (func, fname, line)
                    print "    " + styled(code, "light_gray")

    @classmethod
    def install(cls):
        Connection.setstate = setstate

    @classmethod
    def uninstall():
        Connection.setstate = base_setstate


base_setstate = Connection.setstate

def setstate(self, obj):
    debugger = getattr(_thread_data, "debugger", None)
    if debugger is not None:
        if (
            debugger.filter is None
            or debugger.filter == obj.__class__.__name__
        ):
            if debugger.action == "count":
                debugger.count[obj.__class__] += 1
            elif debugger.action == "blame":
                cls_count = debugger.blame[obj.__class__]
                cls_count[tuple(traceback.extract_stack())] += 1
            elif debugger.action == "interrupt":
                raise Exception(
                    "Someone has requested the state for an instance of class "
                    "%s; interrupting." % obj.__class__
                )

    return base_setstate(self, obj)

