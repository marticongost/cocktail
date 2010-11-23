#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase


class MultipleValuesIndexTestCase(TestCase):

    pairs = (
        (1, "foo"),
        (2, "bar"),
        (2, "bar2"),
        (3, "spam"),
        (4, "sprunge"),
        (4, "sprunge2"),
        (4, "sprunge3")
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
            [(2, "bar"),
             (2, "bar2"),
             (3, "spam"),
             (4, "sprunge"),
             (4, "sprunge2"),
             (4, "sprunge3")],
            min = 2, exclude_min = False)

    def test_supports_ranges_with_excluded_min(self):
        self.assert_range(
            [(3, "spam"),
             (4, "sprunge"),
             (4, "sprunge2"),
             (4, "sprunge3")],
            min = 2, exclude_min = True)

    def test_supports_ranges_with_included_max(self):
        self.assert_range(
            [(1, "foo"),
             (2, "bar"),
             (2, "bar2"),
             (3, "spam")],            
            max = 3, exclude_max = False)

    def test_supports_ranges_with_excluded_max(self):
        self.assert_range(
            [(1, "foo"),
             (2, "bar"),
             (2, "bar2")],            
            max = 3, exclude_max = True)

    def test_supports_ranges_with_both_min_and_max(self):
        self.assert_range(
            [(2, "bar"),
             (2, "bar2"),
             (3, "spam")],
            min = 2,
            exclude_min = False,
            max = 3,
            exclude_max = False
        )

    def test_reports_length(self):
        key_count = len(self.keys)
        assert len(self.index) == key_count

        new_key = self.keys[-1] + 1
        self.index.add(new_key, "new_value")
        assert len(self.index) == key_count + 1

        self.index.remove(new_key, "new_value")
        assert len(self.index) == key_count

    def test_can_retrieve_max_key(self):
        assert self.index.max_key() == 4

    def test_can_retrieve_min_key(self):
        assert self.index.min_key() == 1


class SingleValueIndexTestCase(TestCase):

    pairs = (
        (1, "foo"),
        (2, "bar"),
        (3, "spam"),
        (4, "sprunge"),
        (5, "hum"),
        (6, "krong")
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
            [(2, "bar"),
             (3, "spam"),
             (4, "sprunge"),
             (5, "hum"),
             (6, "krong")],
            min = 2, exclude_min = False)

    def test_supports_ranges_with_excluded_min(self):
        self.assert_range(
            [(3, "spam"),
             (4, "sprunge"),
             (5, "hum"),
             (6, "krong")],
            min = 2, exclude_min = True)

    def test_supports_ranges_with_included_max(self):
        self.assert_range(
            [(1, "foo"),
             (2, "bar"),
             (3, "spam")],
            max = 3, exclude_max = False)

    def test_supports_ranges_with_excluded_max(self):
        self.assert_range(
            [(1, "foo"),
             (2, "bar")],
            max = 3, exclude_max = True)

    def test_supports_ranges_with_both_min_and_max(self):
        self.assert_range(
            [(2, "bar"),
             (3, "spam"),
             (4, "sprunge")],
            min = 2,
            exclude_min = False,
            max = 4,
            exclude_max = False
        )

    def test_reports_length(self):
        key_count = len(self.keys)
        assert len(self.index) == key_count

        new_key = self.keys[-1] + 1
        self.index.add(new_key, "new_value")
        assert len(self.index) == key_count + 1

    def test_can_retrieve_max_key(self):
        assert self.index.max_key() == 6

    def test_can_retrieve_min_key(self):
        assert self.index.min_key() == 1

    def test_adding_an_existing_key_overwrites_the_previous_value(self):
        key, prev_value = self.pairs[0]
        self.index.add(key, "new_value")
        assert self.index[key] == "new_value"
        assert prev_value not in list(self.index.values())

    def test_can_remove_entries_by_key(self):
        self.index.remove(self.keys[0])
        assert self.keys[0] not in list(self.index.keys())
        assert self.values[0] not in list(self.index.values())

