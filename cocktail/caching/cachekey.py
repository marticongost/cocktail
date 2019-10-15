"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Iterable, Mapping, Union, Tuple

CacheKey = Union[str, Tuple[str, ...]]

CacheKeySource = Union[
    str,
    Iterable["CacheKeySource"],
    Mapping["CacheKeySource", "CacheKeySource"]
]

