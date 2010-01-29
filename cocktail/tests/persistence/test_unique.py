#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin

class UniqueTestCase(TempStorageMixin, TestCase):
    
    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail.schema import String
        from cocktail.persistence import PersistentObject

        class Foo(PersistentObject):
            spam = String(
                unique = True,
                indexed = True
            )
        
        class Bar(Foo):
            pass

        self.Foo = Foo
        self.Bar = Bar

    def duplicated(self, obj):
        from cocktail.persistence import UniqueValueError
        return any(
            isinstance(error, UniqueValueError)
            for error in obj.__class__.get_errors(obj)
        )

    def test_validate_self_is_distinct(self):

        a = self.Foo()
        a.spam = "A"
        a.insert()

        assert not self.duplicated(a)

    def test_validate_distinct(self):
        
        a = self.Foo()
        a.spam = "A"
        a.insert()
        
        b = self.Foo()
        b.spam = "B"
        assert not self.duplicated(b)

    def test_validate_duplicate(self):

        a = self.Foo()
        a.spam = "A"
        a.insert()
        
        b = self.Foo()
        b.spam = "A"
        assert self.duplicated(b)

    def test_validate_duplicate_with_inheritance(self):

        a = self.Foo()
        a.spam = "A"
        a.insert()
        
        b = self.Bar()
        b.spam = "A"
        assert self.duplicated(b)

