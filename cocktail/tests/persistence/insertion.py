#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from unittest import TestCase

class InsertionTestCase(TestCase):
    
    def setUp(self):
        
        from os.path import join        
        from tempfile import mkdtemp
        from ZODB.FileStorage import FileStorage
        from cocktail.persistence import datastore
        from cocktail.schema import String, Reference, Collection
        from cocktail.persistence import PersistentObject

        self._temp_dir = mkdtemp()
        datastore.storage = FileStorage(join(self._temp_dir, "testdb.fs"))

        class TestObject(PersistentObject):
            test_field = String(
                unique = True,
                indexed = True
            )
            test_ref = Reference()
            test_collection = Collection()
        
        self.test_type = TestObject

    def tearDown(self):
        from cocktail.persistence import datastore
        from shutil import rmtree
        datastore.abort()
        datastore.close()
        rmtree(self._temp_dir)
    
    def test_inserted_property(self):
        
        instance = self.test_type()
        
        self.assertFalse(instance.inserted)
        instance.insert()
        self.assertTrue(instance.inserted)
    
    def test_insert_twice(self):

        instance = self.test_type()

        # Store an object twice
        instance.insert()
        instance.insert()

    def test_id_acquisition(self):
        instance = self.test_type()
        self.assertTrue(isinstance(instance.id, int))

    def test_indexing(self):
        
        instance = self.test_type()
        instance.test_field = "foo"
        
        self.assertFalse(self.test_type.test_field.index)
        
        instance.insert()
        self.assertEquals(
            list(self.test_type.test_field.index.items()),
            [("foo", instance)]
        )
        
        instance.test_field = "bar"
        self.assertEquals(
            list(self.test_type.test_field.index.items()),
            [("bar", instance)]
        )

    def test_insert_related(self):
                
        instances = [self.test_type()  for i in range(6)]
        
        instances[0].test_ref = instances[1]
        instances[1].test_ref = instances[0]
        instances[0].test_collection = [instances[2], instances[3]]
        instances[2].test_ref = instances[4]
        instances[4].test_collection.append(instances[5])
        
        instances[0].insert()
        self.assertTrue(all(instance.inserted for instance in instances))
        self.assertEqual(len(self.test_type.index), len(instances))
        self.assertEqual(set(self.test_type.index.values()), set(instances))
    
    def test_insert_related_block(self):
        
        a = self.test_type()
        b = self.test_type()
        c = self.test_type()

        b.insert()

        a.test_ref = b
        b.test_ref = c
        a.insert()

        self.assertFalse(c.inserted)

