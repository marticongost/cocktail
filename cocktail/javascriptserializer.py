#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import Mapping, Sequence
import json


class JS(unicode):
    pass


def dumps(value):

    chunks = []

    if isinstance(value, JS):
        return unicode(value)

    if isinstance(value, Mapping):
        return u"{%s}" % u",".join(
            u"%s: %s" % (dumps(k), dumps(v))
            for k, v in value.iteritems()
        )

    if isinstance(value, Sequence) and not isinstance(value, basestring):
        return u"[%s]" % u",".join(dumps(item) for item in value)

    return json.dumps(value)

