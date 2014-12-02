#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from unittest import TestCase
from cocktail.tests.utils import EventLog
from nose.tools import assert_raises


class SchemaEventsTestCase(TestCase):

    def test_member_added_event(self):

        from cocktail.schema import Schema, String
        
        foo = Schema("foo")
        spam = Schema("spam")
        spam.inherit(foo)

        events = EventLog()
        events.listen(foo.member_added, spam.member_added)

        bar = String("bar")
        foo.add_member(bar)

        scrum = String("scrum")
        foo.add_member(scrum)

        event = events.pop(0)
        self.assertEqual(event.slot, foo.member_added)
        self.assertEqual(event.member, bar)

        event = events.pop(0)
        self.assertEqual(event.slot, foo.member_added)
        self.assertEqual(event.member, scrum)

        self.assertFalse(events)

    def test_inherited_event(self):

        from cocktail.schema import Schema

        foo = Schema()
        events = EventLog()
        events.listen(foo_inherited = foo.inherited)

        # Basic inheritance
        bar = Schema()
        bar.inherit(foo)

        event = events.pop(0)
        self.assertEqual(event.slot, foo.inherited)
        self.assertEqual(event.schema, bar)
        
        events.listen(bar_inherited = bar.inherited)

        # Nested inheritance
        spam = Schema()
        spam.inherit(bar)

        event = events.pop(0)
        self.assertEqual(event.slot, foo.inherited)
        self.assertEqual(event.schema, spam)

        event = events.pop(0)
        self.assertEqual(event.slot, bar.inherited)
        self.assertEqual(event.schema, spam)

        # Multiple inheritance
        scrum = Schema()

        events.listen(scrum_inherited = scrum.inherited)

        snutch = Schema()
        snutch.inherit(foo, scrum)
        
        event = events.pop(0)
        self.assertEqual(event.slot, foo.inherited)
        self.assertEqual(event.schema, snutch)

        event = events.pop(0)
        self.assertEqual(event.slot, scrum.inherited)
        self.assertEqual(event.schema, snutch)


class SchemaGroupsTestCase(TestCase):

    def test_grouped_members(self):

        from cocktail.schema import Schema, Member

        a1 = Member("a1", member_group = "a")
        a2 = Member("a2", member_group = "a")
        b1 = Member("b1", member_group = "b")
        b2 = Member("b2", member_group = "b")
        z = Member("z")
        
        schema = Schema(members = [a1, b2, a2, z, b1])
        schema.members_order = ["a2", "a1", "b2", "b1"]
        schema.groups_order = "a", "b"
        
        groups = schema.grouped_members()

        assert len(groups) == 3
        assert all(isinstance(group, tuple) for group in groups)
        assert groups[0][0] == None
        assert groups[1][0] == "a"
        assert groups[2][0] == "b"
        assert list(groups[0][1]) == [z]
        assert list(groups[1][1]) == [a2, a1]
        assert list(groups[2][1]) == [b2, b1]


class MembersOrderTestCase(TestCase):

    def test_preserves_ordering_from_constructor(self):
        
        from cocktail.schema import Schema, Member

        member_list = [Member("m%d" % i) for i in range(5)]
        schema = Schema(members = member_list)
        assert schema.members_order == [m.name for m in member_list]

    def test_follows_explicit_ordering(self):
        
        from cocktail.schema import Schema, Member

        m1 = Member("m1")
        m2 = Member("m2")
        m3 = Member("m3")
        m4 = Member("m4")

        schema = Schema()
        schema.members_order = ["m1", "m4", "m3", "m2"]
        schema.add_member(m1)
        schema.add_member(m2)
        schema.add_member(m3)
        schema.add_member(m4)

        assert schema.ordered_members() == [m1, m4, m3, m2]

    def test_implicitly_includes_unspecified_members(self):
                
        from cocktail.schema import Schema, Member

        m1 = Member("m1")
        m2 = Member("m2")
        m3 = Member("m3")
        m4 = Member("m4")

        schema = Schema()
        schema.members_order = ["m3", "m2"]
        schema.add_member(m1)
        schema.add_member(m2)
        schema.add_member(m3)
        schema.add_member(m4)

        ordered_members = schema.ordered_members()
        assert len(ordered_members) == 4
        assert ordered_members[:2] == [m3, m2]
        assert set(ordered_members[2:]) == set([m1, m4])

    def test_layers_members_from_derived_schemas(self):

        from cocktail.schema import Schema, Member

        b1 = Member("b1")
        b2 = Member("b2")
        b3 = Member("b3")
        b4 = Member("b4")

        b = Schema()
        b.members_order = ["b4", "b3"]
        b.add_member(b1)
        b.add_member(b2)
        b.add_member(b3)
        b.add_member(b4)

        d1 = Member("d1")
        d2 = Member("d2")
        d3 = Member("d3")
        d4 = Member("d4")

        d = Schema()
        d.inherit(b)
        d.members_order = ["d4", "d3"]
        d.add_member(d1)
        d.add_member(d2)
        d.add_member(d3)
        d.add_member(d4)

        mlist = b.ordered_members()
        assert len(mlist) == 4
        assert mlist[:2] == [b4, b3]
        assert set(mlist[2:]) == set([b1, b2])

        mlist = d.ordered_members(False)
        assert len(mlist) == 4
        assert mlist[:2] == [d4, d3]
        assert set(mlist[2:]) == set([d1, d2])

        mlist = d.ordered_members()
        assert len(mlist) == 8
        assert mlist[:2] == [b4, b3]
        assert set(mlist[2:4]) == set([b1, b2])
        assert mlist[4:6] == [d4, d3]
        assert set(mlist[6:]) == set([d1, d2])

    def test_members_can_specify_relative_positions(self):

        from cocktail.schema import Schema, Member

        m1 = Member("m1")
        m2 = Member("m2")
        m3 = Member("m3")
        m4 = Member("m4", after_member = "m5")
        m5 = Member("m5", before_member = "m1")
        m6 = Member("m6", before_member = "m3")

        schema = Schema()
        schema.members_order = ["m3", "m2"]
        schema.add_member(m1)
        schema.add_member(m2)
        schema.add_member(m3)
        schema.add_member(m4)
        schema.add_member(m5)
        schema.add_member(m6)

        ordered_members = schema.ordered_members()
        assert ordered_members == [m6, m3, m2, m5, m4, m1]

    def test_members_can_specify_relative_positions_using_base_schemas(self):

        from cocktail.schema import Schema, Member

        b1 = Member("b1")
        b2 = Member("b2")
        b3 = Member("b3")

        b = Schema()
        b.members_order = ["b2", "b3"]
        b.add_member(b1)
        b.add_member(b2)
        b.add_member(b3)

        d1 = Member("d1")
        d2 = Member("d2", before_member = "b2")
        d3 = Member("d3", after_member = "b1")

        d = Schema()
        d.inherit(b)
        d.add_member(d1)
        d.add_member(d2)
        d.add_member(d3)

        ordered_members = d.ordered_members()
        assert ordered_members == [d2, b2, b3, b1, d3, d1]

    def test_fails_if_member_specifies_conflicting_relative_positions(self):

        from cocktail.schema import Schema, Member

        schema = Schema(members = [
            Member("m1"),
            Member("m2", after_member = "m1", before_member = "m1")
        ])

        assert_raises(ValueError, schema.ordered_members)

    def test_fails_on_cyclic_relative_positions(self):

        from cocktail.schema import Schema, Member

        # Self references
        schema = Schema(members = [
            Member("m1", after_member = "m1")
        ])
        assert_raises(ValueError, schema.ordered_members)

        schema = Schema(members = [
            Member("m1", before_member = "m1")
        ])
        assert_raises(ValueError, schema.ordered_members)

        # 2 step cycle
        schema = Schema(members = [
            Member("m1", before_member = "m2"),
            Member("m2", before_member = "m1")
        ])
        assert_raises(ValueError, schema.ordered_members)

        schema = Schema(members = [
            Member("m1", after_member = "m2"),
            Member("m2", before_member = "m1")
        ])
        assert_raises(ValueError, schema.ordered_members)

        schema = Schema(members = [
            Member("m1", before_member = "m2"),
            Member("m2", after_member = "m1")
        ])
        assert_raises(ValueError, schema.ordered_members)

        schema = Schema(members = [
            Member("m1", after_member = "m2"),
            Member("m2", after_member = "m1")
        ])
        assert_raises(ValueError, schema.ordered_members)

        # 3 step cycle
        schema = Schema(members = [
            Member("m1", before_member = "m3"),
            Member("m2", before_member = "m1"),
            Member("m3", before_member = "m2")
        ])
        assert_raises(ValueError, schema.ordered_members)

    def test_ignores_missing_anchors(self):

        from cocktail.schema import Schema, Member

        m1 = Member("m1", after_member = "m3")
        m2 = Member("m2")

        schema = Schema()
        schema.members_order = ["m2"]
        schema.add_member(m1)
        schema.add_member(m2)
 
        assert schema.ordered_members() == [m2, m1]

