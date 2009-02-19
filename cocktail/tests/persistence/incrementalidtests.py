#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class IncrementalIdTestCase(TempStorageMixin, TestCase):

    def test_acquisition(self):

        from cocktail.persistence import incremental_id
            
        n = 100
        ids = set(incremental_id() for i in range(n))

        self.assertEqual(len(ids), n)

        for id in ids:
            self.assertTrue(id)
            self.assertTrue(isinstance(id, int))
        
    def test_conflict_resolution(self):
        
        from cocktail.persistence import datastore, incremental_id
        datastore.root["foo"] = "bar"
        incremental_id()
        datastore.commit()

