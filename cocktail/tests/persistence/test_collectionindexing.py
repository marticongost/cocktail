#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class StringCollectionIndexing(TempStorageMixin, TestCase):

    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):

            test_collection = schema.Collection(
                items = schema.String(),
                indexed = True
            )

        self.TestObject = TestObject

    def test_inserting_object_updates_index(self):

        a = self.TestObject()
        a.test_collection = ["foo", "bar", "spam"]

        b = self.TestObject()
        b.test_collection = ["foo", "bar"]

        c = self.TestObject()
        c.test_collection = ["foo"]

        index = self.TestObject.test_collection.index

        assert not list(index)

        a.insert()
        assert set(index.items()) == set([
            ("foo", a.id),
            ("bar", a.id),
            ("spam", a.id)
        ])

        b.insert()
        assert set(index.items()) == set([
            ("foo", a.id),
            ("bar", a.id),
            ("spam", a.id),
            ("foo", b.id),
            ("bar", b.id)
        ])

        c.insert()
        assert set(index.items()) == set([
            ("foo", a.id),
            ("bar", a.id),
            ("spam", a.id),
            ("foo", b.id),
            ("bar", b.id),
            ("foo", c.id)
        ])

    def test_deleting_object_updates_index(self):

        a = self.TestObject()
        a.test_collection = ["foo", "bar", "spam"]
        a.insert()

        b = self.TestObject()
        b.test_collection = ["foo", "bar"]
        b.insert()

        c = self.TestObject()
        c.test_collection = ["foo"]
        c.insert()

        index = self.TestObject.test_collection.index

        assert set(index.items()) == set([
            ("foo", a.id),
            ("bar", a.id),
            ("spam", a.id),
            ("foo", b.id),
            ("bar", b.id),
            ("foo", c.id)
        ])

        c.delete()
        assert set(index.items()) == set([
            ("foo", a.id),
            ("bar", a.id),
            ("spam", a.id),
            ("foo", b.id),
            ("bar", b.id)
        ])

        b.delete()
        assert set(index.items()) == set([
            ("foo", a.id),
            ("bar", a.id),
            ("spam", a.id)
        ])

        a.delete()
        assert not list(index)

    def test_adding_items_updates_index(self):

        a = self.TestObject()
        a.insert()

        index = self.TestObject.test_collection.index

        a.test_collection.append("foo")
        assert set(index.items()) == set([
            ("foo", a.id)
        ])

        a.test_collection.append("bar")
        assert set(index.items()) == set([
            ("foo", a.id),
            ("bar", a.id)
        ])

        a.test_collection.append("spam")
        assert set(index.items()) == set([
            ("foo", a.id),
            ("bar", a.id),
            ("spam", a.id)
        ])

    def test_removing_items_updates_index(self):

        a = self.TestObject()
        a.test_collection = ["foo", "bar", "spam"]
        a.insert()

        index = self.TestObject.test_collection.index

        a.test_collection.remove("foo")
        assert set(index.items()) == set([
            ("bar", a.id),
            ("spam", a.id)
        ])

        a.test_collection.remove("bar")
        assert set(index.items()) == set([
            ("spam", a.id)
        ])

        a.test_collection.remove("spam")
        assert not list(index)

    def test_setting_collection_updates_index(self):

        a = self.TestObject()
        a.insert()

        index = self.TestObject.test_collection.index

        a.test_collection = ["foo", "bar"]
        assert set(index.items()) == set([
            ("foo", a.id),
            ("bar", a.id)
        ])

        a.test_collection = ["foo", "spam"]
        assert set(index.items()) == set([
            ("foo", a.id),
            ("spam", a.id)
        ])

        a.test_collection = ["bar"]
        assert set(index.items()) == set([
            ("bar", a.id)
        ])

        a.test_collection = []
        assert not list(index)

    def test_can_rebuild_index(self):

        self.TestObject.test_collection.indexed = False

        a = self.TestObject()
        a.test_collection = ["foo", "bar", "spam"]
        a.insert()

        b = self.TestObject()
        b.test_collection = ["foo", "bar"]
        b.insert()

        c = self.TestObject()
        c.test_collection = ["foo"]
        c.insert()

        self.TestObject.test_collection.indexed = True

        index = self.TestObject.test_collection.index
        assert not list(index)

        self.TestObject.test_collection.rebuild_index()
        index = self.TestObject.test_collection.index

        assert set(index.items()) == set([
            ("foo", a.id),
            ("bar", a.id),
            ("spam", a.id),
            ("foo", b.id),
            ("bar", b.id),
            ("foo", c.id)
        ])


class ReferenceCollectionIndexing(TempStorageMixin, TestCase):

    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class Document(PersistentObject):
            pass

        class Tag(PersistentObject):

            documents = schema.Collection(
                items = schema.Reference(type = Document),
                related_end = schema.Collection("tags",
                    indexed = True
                ),
                indexed = True
            )

        self.Document = Document
        self.Tag = Tag

    def test_inserting_object_updates_index(self):

        Doc = self.Document
        Tag = self.Tag

        d1 = Doc()
        d2 = Doc()
        d3 = Doc()
        d4 = Doc()

        t1 = Tag(); t1.insert()
        t2 = Tag(); t2.insert()
        t3 = Tag(); t3.insert()
        t4 = Tag(); t4.insert()

        d1.tags = [t1, t2, t3, t4]
        d2.tags = [t1, t2, t3]
        d3.tags = [t1, t2]
        d4.tags = [t1]

        index = Doc.tags.index

        assert not list(index)

        d1.insert()
        assert set(index.items()) == set([
            (t1.id, d1.id),
            (t2.id, d1.id),
            (t3.id, d1.id),
            (t4.id, d1.id)
        ])

        d2.insert()
        assert set(index.items()) == set([
            (t1.id, d1.id),
            (t2.id, d1.id),
            (t3.id, d1.id),
            (t4.id, d1.id),
            (t1.id, d2.id),
            (t2.id, d2.id),
            (t3.id, d2.id)
        ])

        d3.insert()
        assert set(index.items()) == set([
            (t1.id, d1.id),
            (t2.id, d1.id),
            (t3.id, d1.id),
            (t4.id, d1.id),
            (t1.id, d2.id),
            (t2.id, d2.id),
            (t3.id, d2.id),
            (t1.id, d3.id),
            (t2.id, d3.id)
        ])

        d4.insert()
        assert set(index.items()) == set([
            (t1.id, d1.id),
            (t2.id, d1.id),
            (t3.id, d1.id),
            (t4.id, d1.id),
            (t1.id, d2.id),
            (t2.id, d2.id),
            (t3.id, d2.id),
            (t1.id, d3.id),
            (t2.id, d3.id),
            (t1.id, d4.id)
        ])

    def test_deleting_object_updates_index(self):

        Doc = self.Document
        Tag = self.Tag

        d1 = Doc(); d1.insert()
        d2 = Doc(); d2.insert()
        d3 = Doc(); d3.insert()
        d4 = Doc(); d4.insert()

        t1 = Tag(); t1.insert()
        t2 = Tag(); t2.insert()
        t3 = Tag(); t3.insert()
        t4 = Tag(); t4.insert()

        d1.tags = [t1, t2, t3, t4]
        d2.tags = [t1, t2, t3]
        d3.tags = [t1, t2]
        d4.tags = [t1]

        index = Doc.tags.index

        assert set(index.items()) == set([
            (t1.id, d1.id),
            (t2.id, d1.id),
            (t3.id, d1.id),
            (t4.id, d1.id),
            (t1.id, d2.id),
            (t2.id, d2.id),
            (t3.id, d2.id),
            (t1.id, d3.id),
            (t2.id, d3.id),
            (t1.id, d4.id)
        ])

        d4.delete()
        assert set(index.items()) == set([
            (t1.id, d1.id),
            (t2.id, d1.id),
            (t3.id, d1.id),
            (t4.id, d1.id),
            (t1.id, d2.id),
            (t2.id, d2.id),
            (t3.id, d2.id),
            (t1.id, d3.id),
            (t2.id, d3.id)
        ])

        d3.delete()
        assert set(index.items()) == set([
            (t1.id, d1.id),
            (t2.id, d1.id),
            (t3.id, d1.id),
            (t4.id, d1.id),
            (t1.id, d2.id),
            (t2.id, d2.id),
            (t3.id, d2.id)
        ])

        d2.delete()
        assert set(index.items()) == set([
            (t1.id, d1.id),
            (t2.id, d1.id),
            (t3.id, d1.id),
            (t4.id, d1.id)
        ])

        d1.delete()
        assert not list(index)

    def test_adding_item_updates_index(self):

        Doc = self.Document
        Tag = self.Tag

        doc = Doc(); doc.insert()
        t1 = Tag(); t1.insert()
        t2 = Tag(); t2.insert()
        t3 = Tag(); t3.insert()
        t4 = Tag(); t4.insert()

        index = Doc.tags.index

        assert not list(index)

        doc.tags.append(t1)
        assert set(index.items()) == set([
            (t1.id, doc.id)
        ])

        doc.tags.append(t2)
        assert set(index.items()) == set([
            (t1.id, doc.id),
            (t2.id, doc.id)
        ])

        doc.tags.append(t3)
        assert set(index.items()) == set([
            (t1.id, doc.id),
            (t2.id, doc.id),
            (t3.id, doc.id)
        ])

        doc.tags.append(t4)
        assert set(index.items()) == set([
            (t1.id, doc.id),
            (t2.id, doc.id),
            (t3.id, doc.id),
            (t4.id, doc.id)
        ])

    def test_removing_item_updates_index(self):

        Doc = self.Document
        Tag = self.Tag

        t1 = Tag(); t1.insert()
        t2 = Tag(); t2.insert()
        t3 = Tag(); t3.insert()
        t4 = Tag(); t4.insert()

        doc = Doc(); doc.insert()
        doc.tags = [t1, t2, t3, t4]

        index = Doc.tags.index

        doc.tags.remove(t4)
        assert set(index.items()) == set([
            (t1.id, doc.id),
            (t2.id, doc.id),
            (t3.id, doc.id)
        ])

        doc.tags.remove(t3)
        assert set(index.items()) == set([
            (t1.id, doc.id),
            (t2.id, doc.id)
        ])

        doc.tags.remove(t2)
        assert set(index.items()) == set([
            (t1.id, doc.id)
        ])

        doc.tags.remove(t1)
        assert not list(index)

    def test_setting_collection_updates_index(self):

        Doc = self.Document
        Tag = self.Tag

        doc = Doc(); doc.insert()
        t1 = Tag(); t1.insert()
        t2 = Tag(); t2.insert()
        t3 = Tag(); t3.insert()
        t4 = Tag(); t4.insert()

        index = Doc.tags.index

        assert not list(index)

        doc.tags = [t1]
        assert set(index.items()) == set([
            (t1.id, doc.id)
        ])

        doc.tags = [t1, t2]
        assert set(index.items()) == set([
            (t1.id, doc.id),
            (t2.id, doc.id)
        ])

        doc.tags = [t2, t3]
        assert set(index.items()) == set([
            (t2.id, doc.id),
            (t3.id, doc.id)
        ])

        doc.tags = [t1, t2, t4]
        assert set(index.items()) == set([
            (t1.id, doc.id),
            (t2.id, doc.id),
            (t4.id, doc.id)
        ])

    def test_can_rebuild_index(self):

        Doc = self.Document
        Tag = self.Tag

        Doc.tags.indexed = False

        d1 = Doc(); d1.insert()
        d2 = Doc(); d2.insert()
        d3 = Doc(); d3.insert()
        d4 = Doc(); d4.insert()

        t1 = Tag(); t1.insert()
        t2 = Tag(); t2.insert()
        t3 = Tag(); t3.insert()
        t4 = Tag(); t4.insert()

        d1.tags = [t1, t2, t3, t4]
        d2.tags = [t1, t2, t3]
        d3.tags = [t1, t2]
        d4.tags = [t1]

        Doc.tags.indexed = True
        index = Doc.tags.index
        assert not list(index)

        Doc.tags.rebuild_index()
        index = Doc.tags.index

        assert set(index.items()) == set([
            (t1.id, d1.id),
            (t2.id, d1.id),
            (t3.id, d1.id),
            (t4.id, d1.id),
            (t1.id, d2.id),
            (t2.id, d2.id),
            (t3.id, d2.id),
            (t1.id, d3.id),
            (t2.id, d3.id),
            (t1.id, d4.id)
        ])

