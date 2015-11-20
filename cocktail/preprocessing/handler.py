#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os


class Handler(object):

    def get_source_mtime(self, file):
        try:
            return os.stat(file.name).st_mtime
        except (IOError, OSError, AttributeError):
            return None

    def get_source(self, file):
        source = file.read()
        return self.process_source(source)

    def process_source(self, source):
        return source

    def get_mime_type(self, file):
        return None

