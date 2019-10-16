"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any


class CacheSerializer:

    def serialize(self, obj: Any) -> bytes:
        raise TypeError(f"{self} doesn't implement the serialize() method")

    def unserialize(self, string: bytes) -> Any:
        raise TypeError(f"{self} doesn't implement the unserialize() method")

