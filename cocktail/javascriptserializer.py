#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import Mapping, Sequence, Set

from . import jsonutils


class JS(str):
    pass


def dumps(value):

    chunks = []

    if isinstance(value, JS):
        return str(value)

    if isinstance(value, Mapping):
        return "{%s}" % ",".join(
            "%s: %s" % (dumps(k), dumps(v))
            for k, v in value.items()
        )

    if isinstance(value, (Sequence, Set)) and not isinstance(value, str):
        return "[%s]" % ",".join(dumps(item) for item in value)

    return jsonutils.dumps(value)

