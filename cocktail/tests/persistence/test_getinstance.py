#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class GetInstanceTests(TempStorageMixin, TestCase):

    def test_get_by_id(self):

        from cocktail.persistence import PersistentObject

        class Foo(PersistentObject):
            pass

        bar = Foo()
        bar.insert()

        spam = Foo()
        spam.insert()

        self.assertEqual(Foo.get_instance(bar.id), bar)
        self.assertEqual(Foo.get_instance(id = bar.id), bar)
        self.assertEqual(Foo.get_instance(spam.id), spam)
        self.assertEqual(Foo.get_instance(id = spam.id), spam)
        self.assertEqual(Foo.get_instance(spam.id + 1), None)

    def test_get_by_indexed_unique_member(self):

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class Foo(PersistentObject):
            foo_name = schema.String(unique = True, indexed = True)

        bar = Foo(foo_name = "bar")
        bar.insert()

        spam = Foo(foo_name = "spam")
        spam.insert()

        self.assertEqual(Foo.get_instance(foo_name = "bar"), bar)
        self.assertEqual(Foo.get_instance(foo_name = "spam"), spam)
        self.assertEqual(Foo.get_instance(foo_name = "scrum"), None)

    def test_get_by_unindexed_unique_member(self):

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class Foo(PersistentObject):
            foo_name = schema.String(unique = True)

        bar = Foo(foo_name = "bar")
        bar.insert()

        spam = Foo(foo_name = "spam")
        spam.insert()

        self.assertEqual(Foo.get_instance(foo_name = "bar"), bar)
        self.assertEqual(Foo.get_instance(foo_name = "spam"), spam)
        self.assertEqual(Foo.get_instance(foo_name = "scrum"), None)

    def test_get_by_regular_member(self):

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class Foo(PersistentObject):
            indexed_foo_name = schema.String()
            unindexed_foo_name = schema.String()

        bar = Foo(
            indexed_foo_name = "bar",
            unindexed_foo_name = "bar"
        )
        bar.insert()

        self.assertRaises(ValueError, Foo.get_instance,
            indexed_foo_name = "bar")

        self.assertRaises(ValueError, Foo.get_instance,
            unindexed_foo_name = "bar")

        self.assertRaises(ValueError, Foo.get_instance,
            indexed_foo_name = "scrum")

        self.assertRaises(ValueError, Foo.get_instance,
            unindexed_foo_name = "scrum")

    def test_get_with_no_criteria(self):

        from cocktail.persistence import PersistentObject

        class Foo(PersistentObject):
            pass

        self.assertRaises(ValueError, Foo.get_instance)

    def test_get_with_no_criteria(self):

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class Foo(PersistentObject):
            foo_name = schema.String(unique = True, indexed = True)
            bar_name = schema.String(unique = True, indexed = True)

        self.assertRaises(ValueError,
            Foo.get_instance,
            foo_name = "foo",
            bar_name = "bar"
        )

    def test_inheritance(self):

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class Foo(PersistentObject):
            foo_name = schema.String(unique = True, indexed = True)

        class Bar(Foo):
            pass

        foo = Foo(foo_name = "foo")
        foo.insert()

        bar = Bar(foo_name = "bar")
        bar.insert()

        self.assertEqual(Bar.get_instance(foo.id), None)
        self.assertEqual(Bar.get_instance(foo_name = "foo"), None)
        self.assertEqual(Bar.get_instance(bar.id), bar)
        self.assertEqual(Bar.get_instance(foo_name = "bar"), bar)

