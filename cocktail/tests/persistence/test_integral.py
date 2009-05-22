#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from unittest import TestCase


class IntegralTestCase(TestCase):

    def test_implicit_cascade_delete(self):
        
        from cocktail.schema import Reference, Collection

        ref = Reference(
            bidirectional = True,
            integral = True
        )
        
        self.assertTrue(ref.cascade_delete)

        collection = Reference(
            bidirectional = True,
            integral = True
        )

        self.assertTrue(collection.cascade_delete)

