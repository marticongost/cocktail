#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase


class IndexTestCase(TestCase):

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
        from cocktail.persistence import Index
        self.index = Index()
        for key, value in self.pairs:
            self.index.add(key, value)

    def assert_range(self, expected_keys, **kwargs):

        expected_values = [value 
                           for key, value in self.pairs 
                           if key in expected_keys]
        
        expected_items = zip(expected_keys, expected_values)

        # Keys
        assert self.index.keys(**kwargs) == expected_keys
        assert list(self.index.iterkeys(**kwargs)) == expected_keys

        # Values
        assert self.index.values(**kwargs) == expected_values
        assert list(self.index.itervalues(**kwargs)) == expected_values

        # Items
        assert self.index.items(**kwargs) == expected_items
        assert list(self.index.iteritems(**kwargs)) == expected_items

    def test_produces_full_sequences(self):
        self.assert_range(self.keys)

    def test_ranges_include_both_ends_by_default(self):
        self.assert_range(
            self.keys,
            min = self.keys[0],
            max = self.keys[-1]
        )

    def test_supports_ranges_with_included_min(self):
        self.assert_range([2, 2, 3, 4, 4, 4], min = 2, excludemin = False)

    def test_supports_ranges_with_excluded_min(self):
        self.assert_range([3, 4, 4, 4], min = 2, excludemin = True)

    def test_supports_ranges_with_included_max(self):
        self.assert_range([1, 2, 2, 3], max = 3, excludemax = False)

    def test_supports_ranges_with_excluded_max(self):
        self.assert_range([1, 2, 2], max = 3, excludemax = True)

    def test_supports_ranges_with_both_min_and_max(self):
        self.assert_range(
            [2, 2, 3],
            min = 2,
            excludemin = False,
            max = 3,
            excludemax = False
        )

    def test_reports_length(self):
        key_count = len(self.keys)
        assert len(self.index) == key_count

        new_key = self.keys[-1] + 1
        self.index.add(new_key, "new_value")
        assert len(self.index) == key_count + 1

        self.index.remove(new_key, "new_value")
        assert len(self.index) == key_count

    def test_supports_indexing_operator(self):
        assert self.index[1] == set(["foo"])
        assert self.index[2] == set(["bar", "bar2"])
        assert self.index[3] == set(["spam"])
        assert self.index[4] == set(["sprunge", "sprunge2", "sprunge3"])

