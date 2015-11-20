#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import mimetypes
from cocktail.caching import Cache, CacheKeyError


class Preprocessors(dict):

    cache = Cache()
    check_source_mtime = True

    def preprocess(self, src_file, mime_type = None):

        if isinstance(src_file, basestring):
            if not mime_type:
                mime_type = mimetypes.guess_type(src_file)[0]
                if not mime_type:
                    return None
                with open(src_file) as src_file:
                    return self.preprocess(src_file, mime_type)

        if not mime_type:
            raise ValueError(
                "Can't preprocess a file without specifying its MIME type"
            )

        handler = self.get(mime_type)
        if handler is None:
            return None

        source = None
        source_mtime = None
        cache_enabled = (self.cache.enabled and self.cache.storage)

        if cache_enabled:
            try:
                entry = self.cache.retrieve(src_file)
            except CacheKeyError:
                pass
            else:
                mime_type, mtime, source = entry
                if self.check_source_mtime:
                    try:
                        source_mtime = handler.get_source_mtime(src_file)
                    except (OSError, IOError):
                        source = None
                    else:
                        if source_mtime > mtime:
                            source = None

        if source is None:
            source = handler.get_source(src_file)
            mime_type = handler.get_mime_type(src_file)
            if cache_enabled:
                if source_mtime is None:
                    source_mtime = handler.get_source_mtime(src_file)
                cache.store(src_file, (mime_type, source_mtime, source))

        return mime_type, source


preprocessors = Preprocessors()

