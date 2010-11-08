#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class FullTextIndexingTestCase(TempStorageMixin, TestCase):
    
    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail.schema import String
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):

            full_text_indexed = True

            field1 = String(
                full_text_indexed = True
            )
            
            field2 = String()
        
        self.test_type = TestObject

    def test_only_indexes_selected_types(self):

        obj = self.test_type()
        self.test_type.full_text_indexed = False
        obj.field1 = u"aaa"
        obj.field2 = u"bbb"
        obj.insert()
        index = self.test_type.get_full_text_index()
        assert index is None

    def test_only_indexes_selected_members(self):

        obj = self.test_type()
        obj.field1 = u"aaa"
        obj.field2 = u"bbb"
        obj.insert()
        
        index = self.test_type.field1.get_full_text_index()
        assert index is not None
        
        index = self.test_type.field2.get_full_text_index()
        assert index is None

    def test_indexes_objects_when_inserted(self):
        
        obj = self.test_type()
        obj.field1 = u"aaa"
        obj.field2 = u"bbb"
        
        index = self.test_type.get_full_text_index()
        index1 = self.test_type.field1.get_full_text_index()

        assert not index.search(u"aaa")
        assert not index.search(u"bbb")
        assert not index1.search(u"aaa")

        obj.insert()

        assert obj.id in index.search(u"aaa")
        assert obj.id in index.search(u"bbb")
        assert obj.id in index1.search(u"aaa")

    def test_reindexes_objects_when_modified(self):
        
        obj = self.test_type()
        obj.insert()
        
        index = self.test_type.get_full_text_index()
        index1 = self.test_type.field1.get_full_text_index()

        # First set of values
        obj.field1 = u"aaa"
        obj.field2 = u"bbb"

        # Second set of values
        obj.field1 = u"yyy"
        obj.field2 = u"zzz"

        assert not index.search(u"aaa")
        assert not index.search(u"bbb")
        assert not index1.search(u"aaa")

        assert obj.id in index.search(u"yyy")
        assert obj.id in index.search(u"zzz")
        assert obj.id in index1.search(u"yyy")

    def test_unindexes_objects_when_deleted(self):

        obj = self.test_type()
        obj.field1 = u"aaa"
        obj.field2 = u"bbb"        
        obj.insert()
        obj.delete()
        
        index = self.test_type.get_full_text_index()
        index1 = self.test_type.field1.get_full_text_index()
        
        assert not index.search(u"aaa")
        assert not index.search(u"bbb")
        assert not index1.search(u"aaa")


class FullTextIndexingTranslationsTestCase(TempStorageMixin, TestCase):
    
    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail.schema import String
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):

            full_text_indexed = True

            field1 = String(
                full_text_indexed = True,
                translated = True
            )
            
            field2 = String(
                translated = True
            )
        
        self.test_type = TestObject

    def test_only_indexes_selected_types(self):

        obj = self.test_type()
        self.test_type.full_text_indexed = False
        obj.set("field1", u"dog", "en")        
        obj.set("field2", u"cat", "en")
        obj.insert()
        index = self.test_type.get_full_text_index("en")
        assert index is None

    def test_only_indexes_selected_members(self):

        obj = self.test_type()
        obj.set("field1", u"dog", "en")
        obj.set("field2", u"cat", "en")
        obj.insert()
        
        index = self.test_type.field1.get_full_text_index("en")
        assert index is not None
        
        index = self.test_type.field2.get_full_text_index("en")
        assert index is None

    def test_indexes_objects_when_inserted(self):
        
        obj = self.test_type()
        obj.set("field1", u"dog", "en")
        obj.set("field2", u"cat", "en")
        
        index = self.test_type.get_full_text_index("en")
        index1 = self.test_type.field1.get_full_text_index("en")

        assert not index.search(u"dog")
        assert not index1.search(u"dog")

        obj.insert()

        assert obj.id in index.search(u"dog")
        assert obj.id in index1.search(u"dog")

    def test_indexes_languages_separetely(self):

        obj = self.test_type()
        obj.set("field1", u"dog", "en")
        obj.set("field2", u"cat", "en")
        obj.set("field1", u"gos", "ca")
        obj.set("field2", u"gat", "ca")
        obj.set("field1", u"perro", "es")
        obj.set("field2", u"gato", "es")
        obj.insert()

        index_en = self.test_type.get_full_text_index("en")
        index1_en = self.test_type.get_full_text_index("en")
        index_ca = self.test_type.get_full_text_index("ca")
        index1_ca = self.test_type.get_full_text_index("ca")
        index_es = self.test_type.get_full_text_index("es")
        index1_es = self.test_type.get_full_text_index("es")

        assert not index_en.search("gos")
        assert not index_en.search("perro")
        assert not index1_en.search("gos")
        assert not index1_en.search("perro")
        assert not index_en.search("gat")
        assert not index_en.search("gato")

        assert not index_ca.search("dog")
        assert not index_ca.search("perro")
        assert not index1_ca.search("dog")
        assert not index1_ca.search("perro")
        assert not index_ca.search("cat")
        assert not index_ca.search("gato")

        assert not index_es.search("dog")
        assert not index_es.search("gos")
        assert not index1_es.search("dog")
        assert not index1_es.search("gos")
        assert not index_es.search("cat")
        assert not index_es.search("gat")

    def test_reindexes_objects_when_modified(self):
        
        obj = self.test_type()
        obj.insert()
                
        # First set of values
        obj.set("field1", u"dog", "en")
        obj.set("field2", u"cat", "en")
        obj.set("field1", u"gos", "ca")
        obj.set("field2", u"gat", "ca")

        # Second set of values
        obj.set("field1", u"wolf", "en")
        obj.set("field2", u"tiger", "en")
        obj.set("field1", u"llop", "ca")
        obj.set("field2", u"tigre", "ca")

        index_en = self.test_type.get_full_text_index("en")
        index1_en = self.test_type.get_full_text_index("en")
        index_ca = self.test_type.get_full_text_index("ca")
        index1_ca = self.test_type.get_full_text_index("ca")

        assert not index_en.search(u"dog")
        assert not index1_en.search(u"dog")
        assert not index_en.search(u"cat")

        assert not index_ca.search(u"gos")
        assert not index1_ca.search(u"gos")
        assert not index_ca.search(u"gat")

        assert obj.id in index_en.search(u"wolf")
        assert obj.id in index1_en.search(u"wolf")
        assert obj.id in index_en.search(u"tiger")

        assert obj.id in index_ca.search(u"llop")
        assert obj.id in index1_ca.search(u"llop")
        assert obj.id in index_ca.search(u"tigre")

    def test_unindexes_objects_when_deleted(self):

        obj = self.test_type()
        obj.set("field1", u"dog", "en")
        obj.set("field1", u"gos", "ca")
        obj.set("field2", u"cat", "en")
        obj.set("field2", u"gat", "ca")
        obj.insert()
        obj.delete()
        
        index_en = self.test_type.get_full_text_index("en")
        index1_en = self.test_type.get_full_text_index("en")
        index_ca = self.test_type.get_full_text_index("ca")
        index1_ca = self.test_type.get_full_text_index("ca")        
        
        assert not index_en.search(u"dog")
        assert not index1_en.search(u"dog")
        assert not index_en.search(u"cat")

        assert not index_ca.search(u"gos")
        assert not index1_ca.search(u"gos")
        assert not index_ca.search(u"gat")


class FullTextIndexingRelationsTestCase(TempStorageMixin, TestCase):
    
    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class A(PersistentObject):
            
            full_text_indexed = True
            
            text = schema.String()
            
            child = schema.Reference(
                bidirectional = True,
                text_search = True
            )
            
            irrelevant_child = schema.Reference(
                bidirectional = True
            )
        
        class B(PersistentObject):
            
            full_text_indexed = True
            
            text = schema.String()
            
            parent = schema.Reference(
                bidirectional = True
            )

            children = schema.Collection(
                bidirectional = True,
                text_search = True
            )
                
        class C(PersistentObject):            
            
            full_text_indexed = True

            text = schema.String()            
            
            parent = schema.Reference(
                bidirectional = True
            )
        
        class Z(PersistentObject):

            text = schema.String()

            parent = schema.Reference(
                bidirectional = True        
            )

        A.child.type = B
        B.parent.type = A
        B.children.items = schema.Reference(type = C)
        C.parent.type = B
        A.irrelevant_child.type = Z
        Z.parent.type = A

        self.A = A
        self.B = B
        self.C = C
        self.Z = Z

    # References
    #--------------------------------------------------------------------------

    def test_only_follows_selected_relations(self):

        a = self.A(text = u"aaa")
        z = self.Z(text = u"zzz")
        a.irrelevant_child = z
        a.insert()

        assert not self.A.get_full_text_index().search("zzz")

    def test_can_index_text_from_references(self):
        
        a = self.A(text = u"aaa")
        b = self.B(text = u"bbb")
        a.child = b
        a.insert()

        assert a.id in self.A.get_full_text_index().search("bbb")

    def test_reindexes_objects_when_reference_changes(self):

        a = self.A(text = u"aaa")
        a.insert()

        b1 = self.B(text = u"bbb1")
        b1.insert()
        
        b2 = self.B(text = u"bbb2")
        b2.insert()

        a.child = b1
        a.child = b2

        index = self.A.get_full_text_index()
        assert not index.search("bbb1")
        assert a.id in index.search("bbb2")

        a.child = None

        assert not index.search("bbb1")
        assert not index.search("bbb2")

    def test_reindexes_objects_when_referred_object_is_modified(self):

        b = self.B(text = u"bbb")
        b.insert()
        a = self.A(text = u"aaa", child = b)        
        a.insert()

        b.text = u"xxx"

        index = self.A.get_full_text_index()
        assert not index.search("bbb")
        assert a.id in index.search("xxx")

    def test_reindexes_objects_when_referred_object_is_deleted(self):

        b = self.B(text = u"bbb")
        b.insert()

        a = self.A(text = u"aaa")
        a.child = b
        a.insert()

        b.delete()

        index = self.A.get_full_text_index()
        assert not index.search("bbb")

    # Collections
    #--------------------------------------------------------------------------

    def test_can_index_text_from_collections(self):
        
        c1 = self.C(text = u"ccc1")
        c2 = self.C(text = u"ccc2")
        c3 = self.C(text = u"ccc3")
        b = self.B(text = u"bbb", children = [c1, c2, c3])
        b.insert()

        index = self.B.get_full_text_index()
        assert b.id in index.search("bbb")
        assert b.id in index.search("ccc1")
        assert b.id in index.search("ccc2")
        assert b.id in index.search("ccc3")

    def test_reindexes_objects_when_collection_item_added(self):

        b = self.B(text = u"bbb")
        b.insert()
        
        c1 = self.C(text = u"ccc1")
        c1.insert()

        c2 = self.C(text = u"ccc2")
        c2.insert()

        c3 = self.C(text = u"ccc3")
        c3.insert()

        index = self.B.get_full_text_index()

        b.children.append(c1)
        assert b.id in index.search("ccc1")

        b.children.append(c2)
        assert b.id in index.search("ccc2")

        b.children.append(c3)
        assert b.id in index.search("ccc3")

    def test_reindexes_objects_when_collection_item_removed(self):

        c1 = self.C(text = u"ccc1")
        c2 = self.C(text = u"ccc2")
        c3 = self.C(text = u"ccc3")
        b = self.B(text = u"bbb", children = [c1, c2, c3])
        b.insert()

        index = self.B.get_full_text_index()

        b.children.remove(c3)
        assert b.id in index.search("ccc1")
        assert b.id in index.search("ccc2")
        assert not index.search("ccc3")

        b.children.remove(c2)
        assert b.id in index.search("ccc1")
        assert not index.search("ccc2")
        assert not index.search("ccc3")

        b.children.remove(c1)
        assert not index.search("ccc1")
        assert not index.search("ccc2")
        assert not index.search("ccc3")

    def test_reindexes_objects_when_collection_is_set_to_none(self):

        c1 = self.C(text = u"ccc1")
        c2 = self.C(text = u"ccc2")
        c3 = self.C(text = u"ccc3")
        b = self.B(text = u"bbb", children = [c1, c2, c3])
        b.insert()

        index = self.B.get_full_text_index()
        b.children = None

        assert not index.search("ccc1")
        assert not index.search("ccc2")
        assert not index.search("ccc3")

    def test_reindexes_objects_when_collection_item_is_deleted(self):

        c1 = self.C(text = u"ccc1")
        c1.insert()

        c2 = self.C(text = u"ccc2")
        c2.insert()

        c3 = self.C(text = u"ccc3")
        c3.insert()

        b = self.B(text = u"bbb", children = [c1, c2, c3])
        b.insert()

        index = self.B.get_full_text_index()

        c3.delete()
        assert b.id in index.search("ccc1")
        assert b.id in index.search("ccc2")
        assert not index.search("ccc3")

        c2.delete()
        assert b.id in index.search("ccc1")
        assert not index.search("ccc2")
        assert not index.search("ccc3")

        c1.delete()
        assert not index.search("ccc1")
        assert not index.search("ccc2")
        assert not index.search("ccc3")

    def test_reindexes_objects_when_collection_item_modified(self):

        c1 = self.C(text = u"ccc1")
        c2 = self.C(text = u"ccc2")
        c3 = self.C(text = u"ccc3")
        b = self.B(text = u"bbb", children = [c1, c2, c3])
        b.insert()

        index = self.B.get_full_text_index()

        c1.text = u"xxx1"
        assert b.id in index.search("xxx1")
        assert not index.search("ccc1")

        c2.text = u"xxx2"
        assert b.id in index.search("xxx2")
        assert not index.search("ccc2")

        c3.text = u"xxx3"
        assert b.id in index.search("xxx3")
        assert not index.search("ccc3")

    def test_follows_relations_recursively(self):

        c = self.C(text = u"ccc")
        b = self.B(text = u"bbb", children = [c])
        a = self.A(text = u"aaa", child = b)
        a.insert()

        index_a = self.A.get_full_text_index()
        index_b = self.B.get_full_text_index()
        index_c = self.C.get_full_text_index()

        assert a.id in index_a.search("aaa")
        assert a.id in index_a.search("bbb")
        assert a.id in index_a.search("ccc")
        
        assert not index_b.search("aaa")
        assert b.id in index_b.search("bbb")
        assert b.id in index_b.search("ccc")

        assert not index_c.search("aaa")
        assert not index_c.search("bbb")
        assert c.id in index_c.search("ccc")

        c.text = "xxx"

        assert not index_a.search("ccc")
        assert not index_b.search("ccc")
        assert not index_c.search("ccc")

        assert a.id in index_a.search("xxx")
        assert b.id in index_b.search("xxx")
        assert c.id in index_c.search("xxx")

