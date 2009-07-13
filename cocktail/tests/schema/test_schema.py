#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from unittest import TestCase
from cocktail.tests.utils import EventLog


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

