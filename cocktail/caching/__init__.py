#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .exceptions import CacheKeyError
from .scope import whole_cache, normalize_scope, resolve_selector
from .cache import Cache
from .cachestorage import CacheStorage
from .cacheserializer import CacheSerializer
from .picklecacheserializer import PickleCacheSerializer
from .memorycachestorage import MemoryCacheStorage
from .restcachestorage import RESTCacheStorage

