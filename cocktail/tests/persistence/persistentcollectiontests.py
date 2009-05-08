#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class PersistentCollectionTestCase(TempStorageMixin, TestCase):

    def test_non_bidirectional_default(self):

        from cocktail.schema import Collection
        from cocktail.persistence import PersistentObject, PersistentList

        class Foo(PersistentObject):
            bar = Collection()
        
        foo = Foo()
        self.assertTrue(isinstance(foo.bar, PersistentList))

    def test_non_bidirectional_assignment(self):

        from cocktail.schema import Collection
        from cocktail.persistence import PersistentObject, PersistentList

        class Foo(PersistentObject):
            bar = Collection()
        
        foo = Foo()
        value = [Foo(), Foo()]
        foo.bar = value
        self.assertTrue(isinstance(foo.bar, PersistentList))
        self.assertEqual(list(foo.bar), value)

    def test_bidirectional_default(self):

        from cocktail.schema import Collection, Reference
        from cocktail.persistence import (
            PersistentObject, PersistentRelationOrderedSet
        )

        class Foo(PersistentObject):
            bar = Collection(bidirectional = True)
        
        class Bar(PersistentObject):
            foo = Reference(bidirectional = True)

        Foo.bar.items = Reference(type = Bar)
        Bar.type = Foo

        foo = Foo()
        self.assertTrue(isinstance(foo.bar, PersistentRelationOrderedSet))
        self.assertTrue(foo.bar.owner is foo)
        self.assertTrue(foo.bar.member is Foo.bar)

    def test_bidirectional_assignment(self):

        from cocktail.schema import Collection, Reference
        from cocktail.persistence import (
            PersistentObject, PersistentRelationOrderedSet
        )

        class Foo(PersistentObject):
            bar = Collection(bidirectional = True)
        
        class Bar(PersistentObject):
            foo = Reference(bidirectional = True)

        Foo.bar.items = Reference(type = Bar)
        Bar.foo.type = Foo

        foo = Foo()
        bar = foo.bar
        value = [Bar(), Bar()]
        foo.bar = value
        self.assertTrue(foo.bar is bar)
        self.assertTrue(isinstance(foo.bar, PersistentRelationOrderedSet))
        self.assertTrue(foo.bar.owner is foo)
        self.assertTrue(foo.bar.member is Foo.bar)
        self.assertEqual(list(foo.bar), value)

