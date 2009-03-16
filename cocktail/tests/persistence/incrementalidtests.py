#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin

# TODO: Test threaded
# TODO: Test multiprocess

class IncrementalIdTestCase(TempStorageMixin, TestCase):

    def test_acquisition(self):

        from cocktail.persistence import incremental_id
       
        n = 100
        ids = set(incremental_id() for i in range(n))

        self.assertEqual(len(ids), n)

        for id in ids:
            self.assertTrue(id)
            self.assertTrue(isinstance(id, int))
 
    def test_multithreaded_acquisition(self):
 
        from cocktail.tests.utils import run_concurrently
        from cocktail.persistence import incremental_id
        
        thread_count = 100
        ids_per_thread = 50
        ids = set()

        def acquisition_thread():
            for i in range(ids_per_thread):
                ids.add(incremental_id())

        run_concurrently(thread_count, acquisition_thread)

        self.assertEqual(len(ids), thread_count * ids_per_thread)

        for id in ids:
            self.assertTrue(id)
            self.assertTrue(isinstance(id, int))

    # TODO: def test_multiprocess_acquisition(self):

    def test_conflict_resolution(self):
        
        from cocktail.persistence import datastore, incremental_id
        datastore.root["foo"] = "bar"
        incremental_id()
        datastore.commit()

