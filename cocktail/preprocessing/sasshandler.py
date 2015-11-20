#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import mimetypes
from .preprocessors import preprocessors
from .handler import Handler

try:
    import sass
except ImportError:
    sass = None


class SASSHandler(Handler):

    def process_source(self, source):
        return sass.compile(string = source)

    def get_mime_type(self, file_path):
        return "text/css"


if sass is not None:
    mimetypes.add_type("text/sass", ".scss")
    preprocessors["text/sass"] = SASSHandler()

