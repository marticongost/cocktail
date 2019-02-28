#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""

class CacheKeyError(Exception):
    """An exception raised when requesting a missing or expired key on a
    :py:attr:`~cocktail.caching.Cache`.
    """

