#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class ModificationTestCase(TempStorageMixin, TestCase):
    
    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail.schema import String
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):
            test_field = String(
                indexed = True
            )
            test_translated_field = String(
                indexed = True,
                translated = True
            )
        
        self.test_type = TestObject

    def test_modifying_member_updates_index(self):
        instance = self.test_type()
        instance.test_field = "foo"
        instance.insert()
        instance.test_field = "bar"
        assert list(self.test_type.test_field.index.items()), [("bar", instance.id)]

    def test_creating_translation_updates_index(self):
        instance = self.test_type()
        instance.insert()

        instance.set("test_translated_field", "foo", "en")

        assert list(self.test_type.test_translated_field.index.items()) == \
            [(("en", "foo"), instance.id)]

    def test_removing_translation_updates_index(self):
        instance = self.test_type()
        instance.set("test_translated_field", "foo", "en")
        instance.insert()

        del instance.translations["en"]

        assert not list(self.test_type.test_translated_field.index.items())
