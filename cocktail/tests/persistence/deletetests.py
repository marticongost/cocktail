#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class DeleteTestCase(TempStorageMixin, TestCase):
    
    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail.schema import String, Reference, Collection
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            test_field = String(
                unique = True,
                indexed = True
            )
        
        self.test_type = TestObject

    def test_delete_not_inserted(self):
        
        from cocktail.persistence import NewObjectDeletedError

        foo = self.test_type()
        self.assertRaises(NewObjectDeletedError, foo.delete)

    def test_delete(self):

        foo = self.test_type()
        foo.insert()
        foo.delete()
        self.assertFalse(foo.is_inserted)

    def test_delete_events(self):

        foo = self.test_type()
        foo.insert()
        events = []

        @foo.deleting.append
        def handle_deleting(event):
            events.append("deleting")
            self.assertTrue(event.source.is_inserted)
        
        @foo.deleted.append
        def handle_deleted(event):
            events.append("deleted")
            self.assertFalse(event.source.is_inserted)

        foo.delete()
        
        self.assertEqual(events, ["deleting", "deleted"])

