#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from unittest import TestCase
from cocktail.tests.utils import EventLog


class ClassFamilyTestCase(TestCase):

    def test_class_family(self):

        from cocktail.schema import Reference
        
        class Foo(object):
            pass

        class Bar(Foo):
            pass

        class Spam(object):
            pass

        ref = Reference(class_family = Foo)

        assert ref.validate(None)
        assert ref.validate(Foo)
        assert ref.validate(Bar)
        assert not ref.validate(Spam)


class OneToOneTestCase(TestCase):

    def get_entities(self):

        from cocktail.schema import SchemaObject
        from cocktail.schema import Reference

        class Foo(SchemaObject):
            bar = Reference(bidirectional = True)

        class Bar(SchemaObject):
            foo = Reference(bidirectional = True)

        Foo.bar.type = Bar
        Bar.foo.type = Foo

        return Foo, Bar

    def test_set_from_constructor(self):
        
        Foo, Bar = self.get_entities()
        foo = Foo()
        bar = Bar(foo = foo)

        self.assertTrue(foo.bar is bar)
        self.assertTrue(bar.foo is foo)

    def test_set(self):

        Foo, Bar = self.get_entities()
        foo = Foo()
        bar = Bar()

        events = EventLog()
        events.listen(
            foo_related = foo.related,
            foo_unrelated = foo.unrelated,
            bar_related = bar.related,
            bar_unrelated = bar.unrelated
        )

        foo.bar = bar

        event = events.pop(0)
        self.assertEqual(event.slot, bar.related)
        self.assertEqual(event.related_object, foo)
        self.assertEqual(event.member, Bar.foo)

        event = events.pop(0)
        self.assertEqual(event.slot, foo.related)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        self.assertFalse(events)

        self.assertTrue(foo.bar is bar)
        self.assertTrue(bar.foo is foo)
        
    def test_set_none(self):

        Foo, Bar = self.get_entities()
        foo = Foo()
        bar = Bar()
        
        # Register test event handlers
        events = EventLog()
        events.listen(
            foo_related = foo.related,
            foo_unrelated = foo.unrelated,
            bar_related = bar.related,
            bar_unrelated = bar.unrelated
        )

        # Set
        foo.bar = bar
        events.clear()

        # Set back to None
        foo.bar = None

        event = events.pop(0)
        self.assertEqual(event.slot, bar.unrelated)
        self.assertEqual(event.related_object, foo)
        self.assertEqual(event.member, Bar.foo)

        event = events.pop(0)
        self.assertEqual(event.slot, foo.unrelated)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        self.assertFalse(events)

        self.assertTrue(foo.bar is None)
        self.assertTrue(bar.foo is None)

        # Try it again from the other side
        foo.bar = bar
        events.clear()

        bar.foo = None
        
        event = events.pop(0)
        self.assertEqual(event.slot, foo.unrelated)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar.unrelated)
        self.assertEqual(event.related_object, foo)
        self.assertEqual(event.member, Bar.foo)

        self.assertFalse(events)

        self.assertTrue(foo.bar is None)
        self.assertTrue(bar.foo is None)

    def test_replace(self):

        Foo, Bar = self.get_entities()
        foo = Foo()
        bar1 = Bar()
        bar2 = Bar()

        # Register test event handlers
        events = EventLog()
        events.listen(
            foo_related = foo.related,
            foo_unrelated = foo.unrelated,
            bar1_related = bar1.related,
            bar1_unrelated = bar1.unrelated,
            bar2_related = bar2.related,
            bar2_unrelated = bar2.unrelated
        )

        foo.bar = bar1
        events.clear()

        # First replacement
        foo.bar = bar2
        
        event = events.pop(0)
        self.assertEqual(event.slot, bar1.unrelated)
        self.assertEqual(event.related_object, foo)
        self.assertEqual(event.member, Bar.foo)

        event = events.pop(0)
        self.assertEqual(event.slot, foo.unrelated)
        self.assertEqual(event.related_object, bar1)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar2.related)
        self.assertEqual(event.related_object, foo)
        self.assertEqual(event.member, Bar.foo)

        event = events.pop(0)
        self.assertEqual(event.slot, foo.related)
        self.assertEqual(event.related_object, bar2)
        self.assertEqual(event.member, Foo.bar)

        self.assertFalse(events)

        self.assertTrue(foo.bar is bar2)
        self.assertTrue(bar1.foo is None)
        self.assertTrue(bar2.foo is foo)

        # Second replacement
        bar1.foo = foo

        event = events.pop(0)
        self.assertEqual(event.slot, bar2.unrelated)
        self.assertEqual(event.related_object, foo)
        self.assertEqual(event.member, Bar.foo)

        event = events.pop(0)
        self.assertEqual(event.slot, foo.unrelated)
        self.assertEqual(event.related_object, bar2)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, foo.related)
        self.assertEqual(event.related_object, bar1)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar1.related)
        self.assertEqual(event.related_object, foo)
        self.assertEqual(event.member, Bar.foo)

        self.assertFalse(events)

        self.assertTrue(foo.bar is bar1)
        self.assertTrue(bar1.foo is foo)
        self.assertTrue(bar2.foo is None)
        

class OneToManyTestCase(TestCase):

    def get_entities(self):

        from cocktail.schema import SchemaObject, Reference, Collection

        class Foo(SchemaObject):
            bar = Reference(bidirectional = True)

        class Bar(SchemaObject):
            foos = Collection(bidirectional = True)

        Foo.bar.type = Bar
        Bar.foos.items = Reference(type = Foo)

        return Foo, Bar

    def test_set_collection_from_constructor(self):

        Foo, Bar = self.get_entities()

        foo = Foo()
        bar = Bar(foos = [foo])

        assert foo.bar is bar
        assert bar.foos == [foo]

    def test_set_reference_from_constructor(self):

        Foo, Bar = self.get_entities()

        bar = Bar()
        foo = Foo(bar = bar)

        assert foo.bar is bar
        assert bar.foos == [foo]

    def test_set(self):
        
        Foo, Bar = self.get_entities()

        foo1 = Foo()
        foo2 = Foo()
        bar = Bar()

        events = EventLog()
        events.listen(
            foo1_related = foo1.related,
            foo1_unrelated = foo1.unrelated,
            foo2_related = foo2.related,
            foo2_unrelated = foo2.unrelated,
            bar_related = bar.related,
            bar_unrelated = bar.unrelated,
        )

        foo1.bar = bar

        event = events.pop(0)
        self.assertEqual(event.slot, bar.related)
        self.assertEqual(event.related_object, foo1)
        self.assertEqual(event.member, Bar.foos)

        event = events.pop(0)
        self.assertEqual(event.slot, foo1.related)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        self.assertFalse(events)
        
        self.assertTrue(foo1.bar is bar)
        self.assertEqual(bar.foos, [foo1])

        foo2.bar = bar
        
        event = events.pop(0)
        self.assertEqual(event.slot, bar.related)
        self.assertEqual(event.related_object, foo2)
        self.assertEqual(event.member, Bar.foos)

        event = events.pop(0)
        self.assertEqual(event.slot, foo2.related)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        self.assertFalse(events)
        
        self.assertTrue(foo1.bar is bar)
        self.assertTrue(foo2.bar is bar)
        self.assertEqual(bar.foos, [foo1, foo2])

    def test_append(self):

        Foo, Bar = self.get_entities()
        
        foo1 = Foo()
        foo2 = Foo()
        
        bar = Bar()

        events = EventLog()
        events.listen(
            foo1_related = foo1.related,
            foo1_unrelated = foo1.unrelated,
            foo2_related = foo2.related,
            foo2_unrelated = foo2.unrelated,
            bar_related = bar.related,
            bar_unrelated = bar.unrelated,
        )

        bar.foos = []

        bar.foos.append(foo1)
        
        event = events.pop(0)
        self.assertEqual(event.slot, foo1.related)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar.related)
        self.assertEqual(event.related_object, foo1)
        self.assertEqual(event.member, Bar.foos)

        self.assertFalse(events)

        self.assertTrue(foo1.bar is bar)
        self.assertEqual(bar.foos, [foo1])

        bar.foos.append(foo2)

        event = events.pop(0)
        self.assertEqual(event.slot, foo2.related)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar.related)
        self.assertEqual(event.related_object, foo2)
        self.assertEqual(event.member, Bar.foos)

        self.assertFalse(events)

        self.assertTrue(foo1.bar is bar)
        self.assertTrue(foo2.bar is bar)
        self.assertEqual(bar.foos, [foo1, foo2])

    def test_set_none(self):

        Foo, Bar = self.get_entities()

        bar = Bar()
        foo1 = Foo()
        foo2 = Foo()

        events = EventLog()
        events.listen(
            foo1_related = foo1.related,
            foo1_unrelated = foo1.unrelated,
            foo2_related = foo2.related,
            foo2_unrelated = foo2.unrelated,
            bar_related = bar.related,
            bar_unrelated = bar.unrelated,
        )

        foo1.bar = bar
        foo2.bar = bar
        events.clear()
        
        foo1.bar = None

        event = events.pop(0)
        self.assertEqual(event.slot, bar.unrelated)
        self.assertEqual(event.related_object, foo1)
        self.assertEqual(event.member, Bar.foos)

        event = events.pop(0)
        self.assertEqual(event.slot, foo1.unrelated)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        self.assertFalse(events)

        self.assertTrue(foo1.bar is None)
        self.assertTrue(foo2.bar is bar)
        self.assertEqual(bar.foos, [foo2])

        foo2.bar = None

        event = events.pop(0)
        self.assertEqual(event.slot, bar.unrelated)
        self.assertEqual(event.related_object, foo2)
        self.assertEqual(event.member, Bar.foos)

        event = events.pop(0)
        self.assertEqual(event.slot, foo2.unrelated)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        self.assertFalse(events)

        self.assertTrue(foo1.bar is None)
        self.assertTrue(foo2.bar is None)
        self.assertEqual(bar.foos, [])

    def test_remove(self):

        Foo, Bar = self.get_entities()

        bar = Bar()
        foo1 = Foo()
        foo2 = Foo()

        events = EventLog()
        events.listen(
            foo1_related = foo1.related,
            foo1_unrelated = foo1.unrelated,
            foo2_related = foo2.related,
            foo2_unrelated = foo2.unrelated,
            bar_related = bar.related,
            bar_unrelated = bar.unrelated,
        )

        foo1.bar = bar
        foo2.bar = bar
        events.clear()

        bar.foos.remove(foo1)

        event = events.pop(0)
        self.assertEqual(event.slot, foo1.unrelated)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar.unrelated)
        self.assertEqual(event.related_object, foo1)
        self.assertEqual(event.member, Bar.foos)

        self.assertFalse(events)

        self.assertTrue(foo1.bar is None)
        self.assertTrue(foo2.bar is bar)
        self.assertEqual(bar.foos, [foo2])

        bar.foos.remove(foo2)

        event = events.pop(0)
        self.assertEqual(event.slot, foo2.unrelated)
        self.assertEqual(event.related_object, bar)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar.unrelated)
        self.assertEqual(event.related_object, foo2)
        self.assertEqual(event.member, Bar.foos)

        self.assertFalse(events)

        self.assertTrue(foo1.bar is None)
        self.assertTrue(foo2.bar is None)
        self.assertEqual(bar.foos, [])

    def test_replace(self):
        
        Foo, Bar = self.get_entities()

        bar1 = Bar()
        bar2 = Bar()
        foo1 = Foo()
        foo2 = Foo()

        events = EventLog()
        events.listen(
            foo1_related = foo1.related,
            foo1_unrelated = foo1.unrelated,
            foo2_related = foo2.related,
            foo2_unrelated = foo2.unrelated,
            bar1_related = bar1.related,
            bar1_unrelated = bar1.unrelated,
            bar2_related = bar2.related,
            bar2_unrelated = bar2.unrelated
        )

        foo1.bar = bar1
        foo2.bar = bar1
        events.clear()

        # First replacement
        foo1.bar = bar2

        event = events.pop(0)
        self.assertEqual(event.slot, bar1.unrelated)
        self.assertEqual(event.related_object, foo1)
        self.assertEqual(event.member, Bar.foos)

        event = events.pop(0)
        self.assertEqual(event.slot, foo1.unrelated)
        self.assertEqual(event.related_object, bar1)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar2.related)
        self.assertEqual(event.related_object, foo1)
        self.assertEqual(event.member, Bar.foos)

        event = events.pop(0)
        self.assertEqual(event.slot, foo1.related)
        self.assertEqual(event.related_object, bar2)
        self.assertEqual(event.member, Foo.bar)

        self.assertFalse(events)

        self.assertTrue(foo1.bar is bar2)
        self.assertTrue(foo2.bar is bar1)
        self.assertEqual(bar1.foos, [foo2])
        self.assertEqual(bar2.foos, [foo1])

        # Second replacement
        foo2.bar = bar2

        event = events.pop(0)
        self.assertEqual(event.slot, bar1.unrelated)
        self.assertEqual(event.related_object, foo2)
        self.assertEqual(event.member, Bar.foos)

        event = events.pop(0)
        self.assertEqual(event.slot, foo2.unrelated)
        self.assertEqual(event.related_object, bar1)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar2.related)
        self.assertEqual(event.related_object, foo2)
        self.assertEqual(event.member, Bar.foos)

        event = events.pop(0)
        self.assertEqual(event.slot, foo2.related)
        self.assertEqual(event.related_object, bar2)
        self.assertEqual(event.member, Foo.bar)

        self.assertFalse(events)

        self.assertTrue(foo1.bar is bar2)
        self.assertTrue(foo2.bar is bar2)
        self.assertEqual(bar1.foos, [])
        self.assertEqual(bar2.foos, [foo1, foo2])

    def test_replace_appending(self):
        
        Foo, Bar = self.get_entities()

        bar1 = Bar()
        bar2 = Bar()
        foo1 = Foo()
        foo2 = Foo()

        events = EventLog()
        events.listen(
            foo1_related = foo1.related,
            foo1_unrelated = foo1.unrelated,
            foo2_related = foo2.related,
            foo2_unrelated = foo2.unrelated,
            bar1_related = bar1.related,
            bar1_unrelated = bar1.unrelated,
            bar2_related = bar2.related,
            bar2_unrelated = bar2.unrelated
        )

        foo1.bar = bar1
        foo2.bar = bar1

        events.clear()

        # First replacement
        bar2.foos.append(foo1)

        event = events.pop(0)
        self.assertEqual(event.slot, bar1.unrelated)
        self.assertEqual(event.related_object, foo1)
        self.assertEqual(event.member, Bar.foos)

        event = events.pop(0)
        self.assertEqual(event.slot, foo1.unrelated)
        self.assertEqual(event.related_object, bar1)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, foo1.related)
        self.assertEqual(event.related_object, bar2)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar2.related)
        self.assertEqual(event.related_object, foo1)
        self.assertEqual(event.member, Bar.foos)

        self.assertFalse(events)

        self.assertTrue(foo1.bar is bar2)
        self.assertTrue(foo2.bar is bar1)
        self.assertEqual(bar1.foos, [foo2])
        self.assertEqual(bar2.foos, [foo1])

        # Second replacement
        bar2.foos.append(foo2)

        event = events.pop(0)
        self.assertEqual(event.slot, bar1.unrelated)
        self.assertEqual(event.related_object, foo2)
        self.assertEqual(event.member, Bar.foos)

        event = events.pop(0)
        self.assertEqual(event.slot, foo2.unrelated)
        self.assertEqual(event.related_object, bar1)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, foo2.related)
        self.assertEqual(event.related_object, bar2)
        self.assertEqual(event.member, Foo.bar)

        event = events.pop(0)
        self.assertEqual(event.slot, bar2.related)
        self.assertEqual(event.related_object, foo2)
        self.assertEqual(event.member, Bar.foos)

        self.assertFalse(events)

        self.assertTrue(foo1.bar is bar2)
        self.assertTrue(foo2.bar is bar2)
        self.assertEqual(bar1.foos, [])
        self.assertEqual(bar2.foos, [foo1, foo2])


class RecursiveRelationTestCase(TestCase):

    def get_schema(self):

        from cocktail.schema import Schema, Reference, Collection

        schema = Schema()
        
        schema.add_member(
            Reference("parent",
                type = schema,
                bidirectional = True
            )
        )

        schema.add_member(
            Collection("children",
                items = Reference(type = schema),
                bidirectional = True
            )
        )

        return schema

    def test_recursive_relation(self):
        
        schema = self.get_schema()

        # Assert that the 'related_end' and 'related_type' properties on both
        # ends of a recursive relation are correctly established
        self.assertEqual(schema["parent"].related_end, schema["children"])
        self.assertEqual(schema["children"].related_end, schema["parent"])
        self.assertEqual(schema["parent"].related_type, schema)
        self.assertEqual(schema["children"].related_type, schema)

    def test_cycles_allowed_declaration(self):

        schema = self.get_schema()

        # Check the default value for the 'cycles_allowed' constraint
        self.assertEqual(schema["parent"].cycles_allowed, True)


class BidirectionalTestCase(TestCase):

    def test_match_one_to_one(self):

        from cocktail.schema import Schema, Reference
        from cocktail.schema.exceptions import SchemaIntegrityError
        
        a = Schema("a")
        b = Schema("b")

        a.add_member(Reference("rel_b", type = b, bidirectional = True))
        b.add_member(Reference("rel_a", type = a, bidirectional = True))

        self.assertTrue(a["rel_b"].related_end is b["rel_a"])
        self.assertTrue(a["rel_b"].related_type is b)
        self.assertTrue(b["rel_a"].related_end is a["rel_b"])
        self.assertTrue(b["rel_a"].related_type is a)

    def test_match_one_to_many(self):

        from cocktail.schema import Schema, Reference, Collection
        from cocktail.schema.exceptions import SchemaIntegrityError
        
        a = Schema("a")
        b = Schema("b")

        a.add_member(Reference("rel_b", type = b, bidirectional = True))
        b.add_member(
            Collection(
                "rel_a",
                items = Reference(type = a),
                bidirectional = True
            )
        )

        self.assertTrue(a["rel_b"].related_end is b["rel_a"])
        self.assertTrue(a["rel_b"].related_type is b)
        self.assertTrue(b["rel_a"].related_end is a["rel_b"])
        self.assertTrue(b["rel_a"].related_type is a)

    def test_match_many_to_many(self):

        from cocktail.schema import Schema, Reference, Collection
        from cocktail.schema.exceptions import SchemaIntegrityError
        
        a = Schema("a")
        b = Schema("b")

        a.add_member(
            Collection(
                "rel_b",
                items = Reference(type = b),
                bidirectional = True
            )
        )
        b.add_member(
            Collection(
                "rel_a",
                items = Reference(type = a),
                bidirectional = True
            )
        )

        self.assertTrue(a["rel_b"].related_end is b["rel_a"])
        self.assertTrue(a["rel_b"].related_type is b)
        self.assertTrue(b["rel_a"].related_end is a["rel_b"])
        self.assertTrue(b["rel_a"].related_type is a)

    def test_no_match(self):

        from cocktail.schema import Schema, Reference
        from cocktail.schema.exceptions import SchemaIntegrityError
        
        a = Schema("a")
        b = Schema("b")

        a.add_member(Reference("rel_b", type = b, bidirectional = True))
        b.add_member(Reference("rel_a", type = a))

        def resolve_relation():
            print a["rel_b"].related_end

        self.assertRaises(SchemaIntegrityError, resolve_relation)
        
        self.assertTrue(b["rel_a"].related_end is None)

    def test_new_related_end(self):

        from cocktail.schema import SchemaObject, Reference

        class Foo(SchemaObject):
            pass

        backref = Reference()

        class Bar(SchemaObject):
            foo = Reference(
                type = Foo,
                related_end = backref
            )

        self.assertTrue(backref.schema is Foo)
        self.assertTrue(backref.name)
        self.assertTrue(getattr(Foo, backref.name) is backref)
        self.assertTrue(Bar.foo.bidirectional)
        self.assertTrue(backref.bidirectional)
        self.assertTrue(Bar.foo.related_end is backref)

    def test_new_related_end_assignment(self):

        from cocktail.schema import SchemaObject, Reference

        class Foo(SchemaObject):
            pass

        backref = Reference()

        class Bar(SchemaObject):
            foo = Reference(type = Foo)

        Bar.foo.related_end = backref

        self.assertTrue(backref.schema is Foo)
        self.assertTrue(backref.name)
        self.assertTrue(getattr(Foo, backref.name) is backref)
        self.assertTrue(Bar.foo.bidirectional)
        self.assertTrue(backref.bidirectional)
        self.assertTrue(Bar.foo.related_end is backref)

    def test_new_related_collection(self):

        from cocktail.schema import SchemaObject, Reference, Collection

        class Foo(SchemaObject):
            pass

        backref = Collection()

        class Bar(SchemaObject):
            foo = Reference(
                type = Foo,
                related_end = backref
            )

        self.assertTrue(backref.schema is Foo)
        self.assertTrue(backref.name)
        self.assertTrue(getattr(Foo, backref.name) is backref)
        self.assertTrue(Bar.foo.bidirectional)
        self.assertTrue(backref.bidirectional)
        self.assertTrue(isinstance(backref.items, Reference))
        self.assertTrue(backref.items.type is Bar)
        self.assertTrue(Bar.foo.related_end is backref)

    def test_new_related_collection_many_to_many(self):

        from cocktail.schema import SchemaObject, Reference, Collection

        class Foo(SchemaObject):
            pass

        backref = Collection()

        class Bar(SchemaObject):
            foo = Collection(
                items = Reference(type = Foo),
                related_end = backref
            )

        self.assertTrue(backref.schema is Foo)
        self.assertTrue(backref.name)
        self.assertTrue(getattr(Foo, backref.name) is backref)
        self.assertTrue(Bar.foo.bidirectional)
        self.assertTrue(backref.bidirectional)
        self.assertTrue(isinstance(backref.items, Reference))
        self.assertTrue(backref.items.type is Bar)
        self.assertTrue(Bar.foo.related_end is backref)

    def test_default(self):

        from cocktail.schema import SchemaObject, Reference, Collection

        class Foo(SchemaObject):
            bars = Collection(
                bidirectional = True
            )

        class Bar(SchemaObject):
            foo = Reference(
                type = Foo,
                bidirectional = True
            )

        Foo.bars.items = Reference(type = Bar)
        default_foo = Foo()
        Bar.foo.default = default_foo

        a = Bar()
        b = Bar()

        assert a.foo is default_foo
        assert b.foo is default_foo
        assert len(default_foo.bars) == 2
        assert set(default_foo.bars) == set([a, b])


class DisabledBidirectionalityTestCase(TestCase):

    def test_one_to_one(self):
        
        from cocktail.schema import SchemaObject, Reference
        from cocktail.schema.exceptions import SchemaIntegrityError
        
        class Foo(SchemaObject):
            pass

        class Bar(SchemaObject):
            pass

        Foo.add_member(Reference("bar", type = Bar, bidirectional = True))
        Bar.add_member(Reference("foo", type = Foo, bidirectional = True))       

        foo = Foo()
        bar = Bar()
        foo.bidirectional = False
        foo.bar = bar

        self.assertTrue(foo.bar is bar)
        self.assertTrue(bar.foo is None)

        bar.foo = foo
        self.assertTrue(bar.foo is foo)
        self.assertTrue(foo.bar is bar)

        foo.bidirectional = True
        foo.bar = None
        self.assertTrue(foo.bar is None)
        self.assertTrue(bar.foo is None)

    def test_one_to_many(self):
        
        from cocktail.schema import SchemaObject, Reference, Collection
        from cocktail.schema.exceptions import SchemaIntegrityError
        
        class Foo(SchemaObject):
            pass

        class Bar(SchemaObject):
            pass

        Foo.add_member(Reference("bar", type = Bar, bidirectional = True))
        Bar.add_member(
            Collection("foos",
                items = Reference(type = Foo),
                bidirectional = True
            )
        )

        foo = Foo()
        bar = Bar()
        foo.bidirectional = False
        foo.bar = bar

        self.assertTrue(foo.bar is bar)
        self.assertFalse(bar.foos)

        bar.foos = [foo]
        self.assertEqual(bar.foos, [foo])
        self.assertTrue(foo.bar is bar)

        foo.bidirectional = True
        foo.bar = None
        self.assertTrue(foo.bar is None)
        self.assertFalse(bar.foos)

        bar.bidirectional = False
        bar.foos = [foo]
        self.assertEqual(bar.foos, [foo])
        self.assertTrue(foo.bar is None)


class IntegralTestCase(TestCase):

    def test_default(self):
        from cocktail.schema import Reference
        self.assertFalse(Reference().integral)

    def test_not_bidirectional(self):
        from cocktail.schema import Reference
        from cocktail.schema.exceptions import SchemaIntegrityError

        # Integral relations must be bidirectional too
        self.assertRaises(SchemaIntegrityError, Reference, integral = True)

    def test_one_to_one(self):

        from cocktail.schema import SchemaObject, Reference
        from cocktail.schema.exceptions import IntegralPartRelocationError

        class TestModel(SchemaObject):
            ref = Reference(
                bidirectional = True,
                integral = True
            )

            backref = Reference(
                bidirectional = True
            )

        TestModel.ref.type = TestModel
        TestModel.backref.type = TestModel

        # Changing the owner of an integral component is not allowed
        a = TestModel()
        b = TestModel()
        c = TestModel()

        a.ref = b

        def change_owner():
            c.ref = b
       
        self.assertRaises(IntegralPartRelocationError, change_owner)
        
        a = TestModel()
        b = TestModel()
        c = TestModel()

        a.ref = b

        def change_owner_reversed():
            b.backref = c

        self.assertRaises(IntegralPartRelocationError, change_owner_reversed)

        # Freeing the integral component is allowed
        a = TestModel()
        b = TestModel()
        a.ref = b
        b.backref = None

    def test_one_to_many(self):

        from cocktail.schema import SchemaObject, Reference, Collection
        from cocktail.schema.exceptions import IntegralPartRelocationError

        class TestModel(SchemaObject):
            parent = Reference(
                bidirectional = True
            )

            children = Collection(
                bidirectional = True,
                integral = True
            )

        TestModel.parent.type = TestModel
        TestModel.children.items = Reference(type = TestModel)

        # Changing the owner of an integral component is not allowed
        a = TestModel()
        b = TestModel()
        c = TestModel()

        a.children.append(b)
        
        def change_owner():
            c.children.append(b)
        
        self.assertRaises(IntegralPartRelocationError, change_owner)

        a = TestModel()
        b = TestModel()
        c = TestModel()

        a.children.append(b)

        def change_owner_reversed():
            b.parent = c
        
        self.assertRaises(IntegralPartRelocationError, change_owner_reversed)

        a = TestModel()
        b = TestModel()
        c = TestModel()

        a.children.append(b)

        def assign_to_new_collection():
            c.children = [b]
        
        self.assertRaises(
            IntegralPartRelocationError,
            assign_to_new_collection)

        # Freeing the integral component is allowed
        a = TestModel()
        b = TestModel()
        a.children.append(b)
        b.parent = None

    def test_many_to_many(self):

        from cocktail.schema import SchemaObject, Reference, Collection
        from cocktail.schema.exceptions import SchemaIntegrityError

        class Container(SchemaObject):
            components = Collection(
                bidirectional = True,
                integral = True
            )

        class Component(SchemaObject):
            containers = Collection(
                bidirectional = True
            )
    
        Container.components.items = Reference(type = Component)
        Component.containers.items = Reference(type = Container)

        # 'integral' can't be set on an n:m relation
        def resolve_relation():
            Container.components.related_end
        
        self.assertRaises(SchemaIntegrityError, resolve_relation)

    def test_both_ends_integral(self):

        from cocktail.schema import SchemaObject, Reference, Collection
        from cocktail.schema.exceptions import SchemaIntegrityError

        class Container(SchemaObject):
            components = Collection(
                bidirectional = True,
                integral = True
            )

        class Component(SchemaObject):
            container = Reference(
                type = Container,
                bidirectional = True,
                integral = True
            )

        Container.components.items = Reference(type = Component)
        
        # 'integral' can't be set on both ends
        def resolve_relation():
            Container.components.related_end
        
        self.assertRaises(SchemaIntegrityError, resolve_relation)

