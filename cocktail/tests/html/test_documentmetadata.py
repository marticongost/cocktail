#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase


class DocumentMetadataTestCase(TestCase):

    def test_ignores_duplicate_resources(self):

        from cocktail.html import Element, DocumentMetadata

        a = Element()
        a.add_resource("/foo.js")

        b = Element()
        b.add_resource("/foo.js")

        metadata = DocumentMetadata()

        metadata.collect(a)
        resources1 = list(metadata.resources)

        metadata.collect(b)
        resources2 = list(metadata.resources)

        assert resources1 == resources2

