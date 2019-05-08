#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class MultipleValuesIndexTestCase(TestCase):

    pairs = (
        ("A", 1),
        ("B", 2),
        ("B", 3),
        ("C", 4),
        ("D", 5),
        ("D", 6),
        ("D", 7)
    )

    keys = []
    values = []

    for key, value in pairs:
        keys.append(key)
        values.append(value)

    def setUp(self):
        from cocktail.persistence import MultipleValuesIndex
        self.index = MultipleValuesIndex()
        for key, value in self.pairs:
            self.index.add(key, value)

    def assert_range(self, expected_items, **kwargs):

        # Items
        from cocktail.persistence.multiplevaluesindex import Entry
        expected_items = [Entry(*item) for item in expected_items]
        assert list(self.index.items(**kwargs)) == expected_items

        # Keys
        expected_keys = [key for key, value in expected_items]
        assert list(self.index.keys(**kwargs)) == expected_keys

        # Values
        expected_values = [value for key, value in expected_items]
        assert list(self.index.values(**kwargs)) == expected_values

        # Descending keys
        kwargs["descending"] = True
        expected_keys.reverse()
        assert list(self.index.keys(**kwargs)) == expected_keys

        # Descending values
        expected_values.reverse()
        assert list(self.index.values(**kwargs)) == expected_values

        # Descending items
        expected_items.reverse()
        assert list(self.index.items(**kwargs)) == expected_items

    def test_produces_full_sequences(self):
        self.assert_range(self.pairs)

    def test_ranges_include_both_ends_by_default(self):
        self.assert_range(
            self.pairs,
            min = self.keys[0],
            max = self.keys[-1]
        )

    def test_supports_ranges_with_included_min(self):
        self.assert_range(
            [("B", 2),
             ("B", 3),
             ("C", 4),
             ("D", 5),
             ("D", 6),
             ("D", 7)],
            min = "B",
            exclude_min = False
        )

    def test_supports_ranges_with_excluded_min(self):
        self.assert_range(
            [("C", 4),
             ("D", 5),
             ("D", 6),
             ("D", 7)],
            min = "B",
            exclude_min = True
        )

    def test_supports_ranges_with_included_max(self):
        self.assert_range(
            [("A", 1),
             ("B", 2),
             ("B", 3),
             ("C", 4)],
            max = "C",
            exclude_max = False
        )

    def test_supports_ranges_with_excluded_max(self):
        self.assert_range(
            [("A", 1),
             ("B", 2),
             ("B", 3)],
            max = "C",
            exclude_max = True
        )

    def test_supports_ranges_with_both_min_and_max(self):
        self.assert_range(
            [("B", 2),
             ("B", 3),
             ("C", 4)],
            min = "B",
            exclude_min = False,
            max = "C",
            exclude_max = False
        )

    def test_reports_length(self):
        key_count = len(self.keys)
        assert len(self.index) == key_count

        new_key = "Z"
        new_value = 1000
        self.index.add(new_key, new_value)
        assert len(self.index) == key_count + 1

        self.index.remove(new_key, new_value)
        assert len(self.index) == key_count

    def test_can_retrieve_max_key(self):
        assert self.index.max_key() == "D"

    def test_can_retrieve_min_key(self):
        assert self.index.min_key() == "A"


class SingleValueIndexTestCase(TestCase):

    pairs = (
        ("A", 1),
        ("B", 2),
        ("C", 3),
        ("D", 4),
        ("E", 5),
        ("F", 6)
    )

    keys = []
    values = []

    for key, value in pairs:
        keys.append(key)
        values.append(value)

    def setUp(self):
        from cocktail.persistence import SingleValueIndex
        self.index = SingleValueIndex()
        for key, value in self.pairs:
            self.index.add(key, value)

    def assert_range(self, expected_items, **kwargs):

        # Keys
        expected_keys = [key for key, value in expected_items]
        assert list(self.index.keys(**kwargs)) == expected_keys

        # Values
        expected_values = [value for key, value in expected_items]
        assert list(self.index.values(**kwargs)) == expected_values

        # Items
        expected_items = list(expected_items)
        assert list(self.index.items(**kwargs)) == expected_items

        # Descending keys
        kwargs["descending"] = True
        expected_keys.reverse()
        rkeys = list(self.index.keys(**kwargs))
        assert list(self.index.keys(**kwargs)) == expected_keys

        # Descending values
        expected_values.reverse()
        assert list(self.index.values(**kwargs)) == expected_values

        # Descending items
        expected_items.reverse()
        assert list(self.index.items(**kwargs)) == expected_items

    def test_produces_full_sequences(self):
        self.assert_range(self.pairs)

    def test_ranges_include_both_ends_by_default(self):
        self.assert_range(
            self.pairs,
            min = self.keys[0],
            max = self.keys[-1]
        )

    def test_supports_ranges_with_included_min(self):
        self.assert_range(
            [("B", 2),
             ("C", 3),
             ("D", 4),
             ("E", 5),
             ("F", 6)],
            min = "B", exclude_min = False)

    def test_supports_ranges_with_excluded_min(self):
        self.assert_range(
            [("C", 3),
             ("D", 4),
             ("E", 5),
             ("F", 6)],
            min = "B", exclude_min = True)

    def test_supports_ranges_with_included_max(self):
        self.assert_range(
            [("A", 1),
             ("B", 2),
             ("C", 3)],
            max = "C", exclude_max = False)

    def test_supports_ranges_with_excluded_max(self):
        self.assert_range(
            [("A", 1),
             ("B", 2)],
            max = "C", exclude_max = True)

    def test_supports_ranges_with_both_min_and_max(self):
        self.assert_range(
            [("B", 2),
             ("C", 3),
             ("D", 4)],
            min = "B",
            exclude_min = False,
            max = "D",
            exclude_max = False
        )

    def test_reports_length(self):
        key_count = len(self.keys)
        assert len(self.index) == key_count

        new_key = "Z"
        new_value = 1000
        self.index.add(new_key, new_value)
        assert len(self.index) == key_count + 1

    def test_can_retrieve_max_key(self):
        assert self.index.max_key() == "F"

    def test_can_retrieve_min_key(self):
        assert self.index.min_key() == "A"

    def test_adding_an_existing_key_overwrites_the_previous_value(self):
        key, prev_value = self.pairs[0]
        self.index.add(key, "new_value")
        assert self.index[key] == "new_value"
        assert prev_value not in list(self.index.values())

    def test_can_remove_entries_by_key(self):
        self.index.remove(self.keys[0])
        assert self.keys[0] not in list(self.index.keys())
        assert self.values[0] not in list(self.index.values())


class TranslationInheritanceIndexingTestCase(TempStorageMixin, TestCase):

    def test_indexing_works_across_derived_translations(self):

        from cocktail.translations import fallback_languages_context
        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):

            test_field = schema.String(
                translated = True,
                indexed = True
            )

        obj = TestObject()
        obj.insert()

        with fallback_languages_context({
            "en-CA": ["en"],
            "fr-CA": ["fr", "en-CA"]
        }):
            obj.set("test_field", "foo", "en")
            assert set(TestObject.test_field.index.items()) == set([
                (("en", "foo"), obj.id),
                (("en-CA", "foo"), obj.id),
                (("fr-CA", "foo"), obj.id)
            ])

            obj.set("test_field", "bar", "fr")
            assert set(TestObject.test_field.index.items()) == set([
                (("en", "foo"), obj.id),
                (("en-CA", "foo"), obj.id),
                (("fr", "bar"), obj.id),
                (("fr-CA", "bar"), obj.id)
            ])

            del obj.translations["fr"]
            print(list(TestObject.test_field.index.items()))
            assert set(TestObject.test_field.index.items()) == set([
                (("en", "foo"), obj.id),
                (("en-CA", "foo"), obj.id),
                (("fr-CA", "foo"), obj.id)
            ])

    def test_no_automatic_reindexing_if_the_language_chain_changes(self):

        from cocktail.translations import fallback_languages_context
        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):

            test_field = schema.String(
                translated = True,
                indexed = True
            )

        obj = TestObject()
        obj.insert()

        with fallback_languages_context({
            "en-CA": ["en"],
            "fr-CA": ["fr", "en-CA"]
        }):
            obj.set("test_field", "foo", "en")
            assert set(TestObject.test_field.index.items()) == set([
                (("en", "foo"), obj.id),
                (("en-CA", "foo"), obj.id),
                (("fr-CA", "foo"), obj.id)
            ])

        with fallback_languages_context({
            "en-CA": ["en"],
            "fr-CA": ["fr"]
        }):
            obj.set("test_field", "foo", "en")
            assert set(TestObject.test_field.index.items()) == set([
                (("en", "foo"), obj.id),
                (("en-CA", "foo"), obj.id),
                (("fr-CA", "foo"), obj.id)
            ])

