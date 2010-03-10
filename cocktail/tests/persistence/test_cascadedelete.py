#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class CascadeDeleteTestCase(TempStorageMixin, TestCase):

    def test_reference(self):

        from cocktail.schema import Reference
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            ref = Reference(cascade_delete = True)

        a = TestObject(ref = TestObject())
        a.insert()
        a.delete()

        self.assertFalse(TestObject.index)

    def test_reference_multilevel(self):

        from cocktail.schema import Reference
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            ref = Reference(cascade_delete = True)

        a = TestObject(ref = TestObject(ref = TestObject()))
        a.insert()
        a.delete()

        self.assertFalse(TestObject.index)

    def test_no_cascade(self):

        from cocktail.schema import Reference
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            ref = Reference()

        a = TestObject()
        a.insert()
        b = TestObject()
        b.insert()

        a.ref = b

        a.delete()
        self.assertEquals(list(TestObject.index.values()), [b])
        
    def test_reference_cycle(self):
        
        from cocktail.schema import Reference
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            ref = Reference(cascade_delete = True)

        a = TestObject()
        a.insert()        
        b = TestObject()
        b.insert()

        a.ref = b
        b.ref = a

        a.delete()
        self.assertFalse(TestObject.index)

    def test_should_cascade_delete_reference(self):

        from cocktail.schema import Reference
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            ref = Reference(cascade_delete = True)

            def _should_cascade_delete(self, member):
                return True

        a = TestObject(ref = TestObject())
        a.insert()
        a.delete()

        assert not TestObject.index

    def test_not_should_cascade_delete_reference(self):

        from cocktail.schema import Reference
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            ref = Reference(cascade_delete = True)

            def _should_cascade_delete(self, member):
                return False

        a = TestObject()
        b = TestObject()
        a.ref = b
        a.insert()
        a.delete()

        assert len(TestObject.index) == 1
        assert set(TestObject.index.values()) == set([b])

    def test_collection(self):

        from cocktail.schema import Collection
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            collection = Collection(cascade_delete = True)

        a = TestObject(collection = [TestObject(), TestObject()])
        a.insert()
        a.delete()

        self.assertFalse(TestObject.index)

    def test_bidirectional_collection(self):

        from cocktail.schema import Collection, Reference
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            
            parent = Reference(
                bidirectional = True
            )
            
            collection = Collection(
                cascade_delete = True,
                bidirectional = True
            )
        
        TestObject.parent.type = TestObject
        TestObject.collection.items = Reference(type = TestObject)

        a = TestObject(collection = [TestObject(), TestObject()])
        a.insert()
        a.delete()

        assert not TestObject.index

    def test_collection_multilevel(self):

        from cocktail.schema import Collection
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            collection = Collection(cascade_delete = True)

        a = TestObject(a = [
            TestObject(),
            TestObject(a = [
                TestObject(),
                TestObject()
            ])
        ])
        a.insert()        
        a.delete()
        self.assertFalse(TestObject.index)

    def test_no_cascade_collection(self):

        from cocktail.schema import Collection
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            collection = Collection()

        a = TestObject()
        b = TestObject()
        c = TestObject()
        a.collection = [b,c]
        a.insert()
        a.delete()

        self.assertEquals(len(TestObject.index), 2)
        self.assertEquals(set(TestObject.index.values()), set([b, c]))
        
    def test_should_cascade_delete_collection(self):

        from cocktail.schema import Collection
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            collection = Collection(cascade_delete = True)

            def _should_cascade_delete(self, member):
                return True

        a = TestObject(collection = [TestObject(), TestObject()])
        a.insert()
        a.delete()

        assert not TestObject.index

    def test_not_should_cascade_delete_collection(self):

        from cocktail.schema import Collection
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            collection = Collection(cascade_delete = True)

            def _should_cascade_delete(self, member):
                return False

        a = TestObject()
        b = TestObject()
        c = TestObject()
        a.collection = [b,c]
        a.insert()
        a.delete()

        assert len(TestObject.index) == 2
        assert set(TestObject.index.values()) == set([b, c])
