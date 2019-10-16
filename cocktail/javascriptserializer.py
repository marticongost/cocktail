"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any, Union
from collections import Mapping, Sequence, Set

from . import jsonutils


class JS(str):
    """A literal snippet of Javascript, to be included as is when calling
    `dumps` to generate Javascript output.
    """


javascript = Union[jsonutils.json_data, JS]


def dumps(value: javascript) -> str:

    if isinstance(value, JS):
        return str(value)

    if isinstance(value, Mapping):
        return "{%s}" % ",".join(
            f"{dumps(k)}: {dumps(v)}" for k, v in value.items()
        )

    if isinstance(value, (Sequence, Set)) and not isinstance(value, str):
        return "[%s]" % ",".join(dumps(item) for item in value)

    return jsonutils.dumps(value)

