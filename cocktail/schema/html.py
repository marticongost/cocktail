#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.stringutils import html_to_plain_text
from cocktail.schema.schemastrings import String


class HTML(String):

    # Initialization parameters for TinyMCE (see cocktail.html.TinyMCE)
    tinymce_params = None

    def extract_searchable_text(self, extractor):
        text = html_to_plain_text(extractor.current.value)
        extractor.feed(text)

