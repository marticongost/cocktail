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
    
    def test_delete_updates_self_contained_relation(self):

        from cocktail.schema import Reference, Collection
        from cocktail.persistence import PersistentObject

        class A(PersistentObject):
            pass

        class B(PersistentObject):
            pass

        A.add_member(
            Collection(
                "b",
                items = Reference(type = B),
                related_end = Collection()
            )
        )

        a = A()
        a.insert()

        b = B()
        b.insert()

        a.b.append(b)        
        b.delete()

        assert not a.b

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


class IndexingDeleteTestCase(TempStorageMixin, TestCase):

    def setUp(self):
        TempStorageMixin.setUp(self)

    def test_delete_clears_regular_member(self):

        from cocktail.schema import String
        from cocktail.persistence import PersistentObject
        
        class TestObject(PersistentObject):
            test_member = String(indexed = True)

        test_object = TestObject()
        test_object.test_member = "test string"
        test_object.insert()
        test_object.delete()

        assert not TestObject.test_member.index

    def test_delete_clears_unique_member(self):

        from cocktail.schema import String
        from cocktail.persistence import PersistentObject
        
        class TestObject(PersistentObject):
            test_member = String(indexed = True, unique = True)

        test_object = TestObject()
        test_object.test_member = "test string"
        test_object.insert()
        test_object.delete()

        assert not TestObject.test_member.index

    def test_delete_clears_translated_member(self):

        from cocktail.schema import String
        from cocktail.persistence import PersistentObject
        
        class TestObject(PersistentObject):
            test_member = String(indexed = True, translated = True)

        test_object = TestObject()
        test_object.set("test_member", "test string", "en")
        test_object.set("test_member", "cadena de prueba", "es")
        test_object.insert()
        test_object.delete()

        assert not TestObject.test_member.index

    def test_delete_clears_unique_translated_member(self):

        from cocktail.schema import String
        from cocktail.persistence import PersistentObject
        
        class TestObject(PersistentObject):
            test_member = String(
                indexed = True,
                unique = True,
                translated = True
            )

        test_object = TestObject()
        test_object.set("test_member", "test string", "en")
        test_object.set("test_member", "cadena de prueba", "es")
        test_object.insert()
        test_object.delete()

        assert not TestObject.test_member.index

    def test_delete_clears_normalized_member(self):

        from cocktail.schema import String
        from cocktail.persistence import PersistentObject
        
        class TestObject(PersistentObject):
            test_member = String(indexed = True, normalized_index = True)

        test_object = TestObject()
        test_object.test_member = "Test String"
        test_object.insert()
        test_object.delete()

        assert not TestObject.test_member.index

