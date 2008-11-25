#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from unittest import TestCase
from glob import glob
from os import remove

class RelationTestCase(TestCase):

    DB_FILE = "relationtests.db"

    def setUp(self):
        from cocktail.persistence import datastore
        from ZODB.FileStorage import FileStorage
        datastore.storage = FileStorage(self.DB_FILE)
        datastore.root.clear()

    def tearDown(self):
        for name in glob(self.DB_FILE + "*"):
            remove(name)

class OneToOneTestCase(RelationTestCase):

    def get_entities(self):

        from cocktail.persistence import Entity
        from cocktail.schema import Reference

        class Foo(Entity):
            bar = Reference(bidirectional = True)

        class Bar(Entity):
            foo = Reference(bidirectional = True)

        Foo.bar.type = Bar
        Bar.foo.type = Foo

        return Foo, Bar

    def test_set(self):

        Foo, Bar = self.get_entities()
        foo = Foo()
        bar = Bar()
        foo.bar = bar

        self.assertTrue(foo.bar is bar)
        self.assertTrue(bar.foo is foo)
        
    def test_set_none(self):

        Foo, Bar = self.get_entities()
        foo = Foo()
        bar = Bar()
        
        foo.bar = bar
        foo.bar = None

        self.assertTrue(foo.bar is None)
        self.assertTrue(bar.foo is None)

        foo.bar = bar
        bar.foo = None

        self.assertTrue(foo.bar is None)
        self.assertTrue(bar.foo is None)

    def test_replace(self):

        Foo, Bar = self.get_entities()
        foo = Foo()
        bar1 = Bar()
        bar2 = Bar()

        foo.bar = bar1
        foo.bar = bar2

        self.assertTrue(foo.bar is bar2)
        self.assertTrue(bar1.foo is None)
        self.assertTrue(bar2.foo is foo)

        bar1.foo = foo
        self.assertTrue(foo.bar is bar1)
        self.assertTrue(bar1.foo is foo)
        self.assertTrue(bar2.foo is None)


class OneToManyTestCase(RelationTestCase):

    def get_entities(self):

        from cocktail.persistence import Entity
        from cocktail.schema import Reference, Collection

        class Foo(Entity):
            bar = Reference(bidirectional = True)

        class Bar(Entity):
            foos = Collection(bidirectional = True)

        Foo.bar.type = Bar
        Bar.foos.items = Reference(type = Foo)

        return Foo, Bar

    def test_set(self):
        
        Foo, Bar = self.get_entities()

        foo1 = Foo()
        foo2 = Foo()
        bar = Bar()

        foo1.bar = bar
        
        self.assertTrue(foo1.bar is bar)
        self.assertEqual(bar.foos, [foo1])

        foo2.bar = bar
        self.assertTrue(foo1.bar is bar)
        self.assertTrue(foo2.bar is bar)
        self.assertEqual(bar.foos, [foo1, foo2])

    def test_append(self):

        Foo, Bar = self.get_entities()
        
        foo1 = Foo()
        foo2 = Foo()
        
        bar = Bar()
        bar.foos = []

        bar.foos.append(foo1)
        
        self.assertTrue(foo1.bar is bar)
        self.assertEqual(bar.foos, [foo1])

        bar.foos.append(foo2)

        self.assertTrue(foo1.bar is bar)
        self.assertTrue(foo2.bar is bar)
        self.assertEqual(bar.foos, [foo1, foo2])

    def test_set_none(self):

        Foo, Bar = self.get_entities()

        bar = Bar()
        foo1 = Foo()
        foo2 = Foo()
        foo1.bar = bar
        foo2.bar = bar

        foo1.bar = None

        self.assertTrue(foo1.bar is None)
        self.assertTrue(foo2.bar is bar)
        self.assertEqual(bar.foos, [foo2])

        foo2.bar = None

        self.assertTrue(foo1.bar is None)
        self.assertTrue(foo2.bar is None)
        self.assertEqual(bar.foos, [])

    def test_remove(self):

        Foo, Bar = self.get_entities()

        bar = Bar()
        foo1 = Foo()
        foo2 = Foo()
        foo1.bar = bar
        foo2.bar = bar

        bar.foos.remove(foo1)

        self.assertTrue(foo1.bar is None)
        self.assertTrue(foo2.bar is bar)
        self.assertEqual(bar.foos, [foo2])

        bar.foos.remove(foo2)

        self.assertTrue(foo1.bar is None)
        self.assertTrue(foo2.bar is None)
        self.assertEqual(bar.foos, [])

    def test_replace(self):
        
        Foo, Bar = self.get_entities()

        bar1 = Bar()
        bar2 = Bar()
        foo1 = Foo()
        foo2 = Foo()

        foo1.bar = bar1
        foo2.bar = bar1

        foo1.bar = bar2
        
        self.assertTrue(foo1.bar is bar2)
        self.assertTrue(foo2.bar is bar1)
        self.assertEqual(bar1.foos, [foo2])
        self.assertEqual(bar2.foos, [foo1])

        foo2.bar = bar2

        self.assertTrue(foo1.bar is bar2)
        self.assertTrue(foo2.bar is bar2)
        self.assertEqual(bar1.foos, [])
        self.assertEqual(bar2.foos, [foo1, foo2])

    def test_replace_appending(self):
        
        Foo, Bar = self.get_entities()

        bar1 = Bar()
        bar2 = Bar()
        foo1 = Foo()
        foo2 = Foo()

        foo1.bar = bar1
        foo2.bar = bar1

        bar2.foos.append(foo1)
        
        self.assertTrue(foo1.bar is bar2)
        self.assertTrue(foo2.bar is bar1)
        self.assertEqual(bar1.foos, [foo2])
        self.assertEqual(bar2.foos, [foo1])

        bar2.foos.append(foo2)

        self.assertTrue(foo1.bar is bar2)
        self.assertTrue(foo2.bar is bar2)
        self.assertEqual(bar1.foos, [])
        self.assertEqual(bar2.foos, [foo1, foo2])

