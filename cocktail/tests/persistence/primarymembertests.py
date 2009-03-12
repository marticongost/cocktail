#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class PrimaryMemberTestCase(TempStorageMixin, TestCase):

    def test_declaration(self):

        from cocktail.schema import Member
        import cocktail.persistence

        pk = Member(primary = True)
        self.assertTrue(pk.unique)
        self.assertTrue(pk.required)

        pk.unique = True
        pk.required = True

        self.assertRaises(TypeError, setattr, pk, "unique", False)
        self.assertRaises(TypeError, setattr, pk, "required", False)

    def test_changing(self):

        from cocktail.persistence.persistentobject import (
            PersistentObject, PrimaryKeyChangedError
        )

        class Foo(PersistentObject):
            pass

        foo = Foo()
        foo.id = 5
        foo.insert()
        foo.id = foo.id
        self.assertRaises(PrimaryKeyChangedError, foo.set, "id", foo.id + 1)

