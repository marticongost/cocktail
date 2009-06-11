#-*- coding: utf-8 -*-
u"""

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
            parent = Reference(bidirectional = True)
            children = Collection(bidirectional = True)

        TestObject.parent.type = TestObject
        TestObject.children.items = Reference(type = TestObject)
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
    
    def test_delete_updates_indexes(self):

        from cocktail.schema import String, Integer
        from cocktail.persistence import PersistentObject
        
        class TestObject(PersistentObject):
            test_string = String(indexed = True)
            test_integer = Integer(indexed = True, unique = True)

        test_object = TestObject()
        test_object.test_string = "test string"
        test_object.test_integer = 3
        test_object.insert()
        test_object.delete()

        assert len(TestObject.test_string.index) == 0
        assert len(TestObject.test_integer.index) == 0

    def test_delete_updates_foreign_reference(self):

        parent = self.test_type()
        parent.insert()

        child = self.test_type()
        child.insert()

        child.parent = parent
        parent.delete()

        self.assertTrue(child.parent is None)

    def test_delete_updates_foreign_collection(self):

        parent = self.test_type()
        parent.insert()

        child = self.test_type()
        child.insert()

        parent.children.append(child)
        child.delete()

        self.assertFalse(parent.children)

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

