#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from unittest import TestCase
from cocktail.tests.utils import EventLog


class DeclarationTestCase(TestCase):

    def test_declaration(self):

        from cocktail.schema import Schema, SchemaObject, String, Integer

        class Foo(SchemaObject):
            bar = String()
            spam = Integer()
        
        self.assertTrue(isinstance(Foo, Schema))
        self.assertTrue(isinstance(Foo.bar, String))
        self.assertTrue(isinstance(Foo.spam, Integer))
        self.assertTrue(Foo.bar is Foo["bar"])
        self.assertTrue(Foo.spam is Foo["spam"])
        self.assertEqual(Foo.members(), {"bar": Foo.bar, "spam": Foo.spam})

    def test_name_clash(self):

        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            spam = None

        self.assertRaises(AttributeError, Foo.add_member, String("spam"))

        class Bar(Foo):
            pass

        self.assertRaises(AttributeError, Foo.add_member, String("spam"))

        for name in (
            "name", "schema", "adaptation_source", "translated", "translation",
            "required", "require_none", "enumeration", "type"
        ):
            self.assertRaises(AttributeError, Foo.add_member, String(name))
            self.assertRaises(AttributeError, Bar.add_member, String(name))
            self.assertRaises(AttributeError,
                type, "Test", (SchemaObject,), {name: String()}
            )

    def test_inheritance(self):
        
        from cocktail.schema import Schema, SchemaObject, String, Integer

        class Foo(SchemaObject):
            foo_a = String()
            foo_b = Integer()

        class Bar(Foo):
            bar_a = String()
            bar_b = Integer()

        # Make sure the base class remains unchanged
        self.assertTrue(isinstance(Foo.foo_a, String))
        self.assertTrue(isinstance(Foo.foo_b, Integer))
        self.assertTrue(Foo.foo_a is Foo["foo_a"])
        self.assertTrue(Foo.foo_b is Foo["foo_b"])
        self.assertEqual(Foo.members(), {
            "foo_a": Foo.foo_a,
            "foo_b": Foo.foo_b
        })
        self.assertRaises(AttributeError, getattr, Foo, "bar_a")
        self.assertRaises(AttributeError, getattr, Foo, "bar_b")
        
        # Check that the derived class correctly defines its members
        self.assertTrue(isinstance(Bar.bar_a, String))
        self.assertTrue(isinstance(Bar.bar_b, Integer))
        self.assertTrue(Bar.bar_a is Bar["bar_a"])
        self.assertTrue(Bar.bar_b is Bar["bar_b"])        
        self.assertEqual(Bar.members(recursive = False), {
            "bar_a": Bar.bar_a,
            "bar_b": Bar.bar_b
        })

        # Assert that the derived class inherits members from its base class
        self.assertTrue(Bar.foo_a is Foo.foo_a)
        self.assertTrue(Bar.foo_b is Foo.foo_b)
        self.assertEqual(Bar.members(), {
            "foo_a": Foo.foo_a,
            "foo_b": Foo.foo_b,
            "bar_a": Bar.bar_a,
            "bar_b": Bar.bar_b
        })
        
        # Inherited members should still refer the base class as their schema
        self.assertTrue(Foo.foo_a.schema is Foo)
        self.assertTrue(Foo.foo_b.schema is Foo)

        # On the other hand, additional members defined by the derived class
        # should refer the derived class as their schema
        self.assertTrue(Bar.bar_a.schema is Bar)
        self.assertTrue(Bar.bar_b.schema is Bar)


class ExtensionTestCase(TestCase):
    
    def test_add_member(self):
        
        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            pass

        new_member = String("bar")
        Foo.add_member(new_member)
        
        self.assertEqual(new_member.schema, Foo)
        self.assertEqual(Foo.bar, new_member)

    def test_inheritance(self):
        
        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            pass

        class Spam(Foo):
            pass

        new_member = String("bar")
        Foo.add_member(new_member)

        self.assertEqual(new_member.schema, Foo)
        self.assertEqual(Spam.bar, new_member)

    def test_retroactive(self):

        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            pass

        foo = Foo()
        Foo.add_member(String("bar", default = "Bar!"))
        self.assertEqual(foo.bar, "Bar!")

    def test_retroactive_per_class_defaults(self):

        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            pass

        class Bar(Foo):
            pass
            
        bar = Bar()
        Foo.add_member(String("spam", default = "Foo!"))
        Bar.default_spam = "Bar!"
        self.assertEqual(bar.spam, "Bar!")


class AttributeTestCase(TestCase):

    def test_instantiation(self):

        from cocktail.schema import Schema, SchemaObject, String, Integer

        class Foo(SchemaObject):
            bar = String(default = "Default bar")
            spam = Integer()

        members = set([Foo.bar, Foo.spam])

        events = EventLog()
        events.listen(
            Foo_instantiated = Foo.instantiated,
            Foo_changed = Foo.changed,
            Foo_changing = Foo.changing
        )

        values = {"bar": "Custom bar", "spam": 3}

        foo = Foo(**values)

        for i in range(len(values)):
            event = events.pop(0)
            member = event.member
            self.assertEqual(event.slot, Foo.changing)
            self.assertEqual(event.value, values[member.name])
            self.assertEqual(event.previous_value, None)

            event = events.pop(0)
            self.assertEqual(event.slot, Foo.changed)
            self.assertEqual(event.member, member)
            self.assertEqual(event.value, values[member.name])
            self.assertEqual(event.previous_value, None)
            members.remove(member)

        event = events.pop(0)
        self.assertEqual(event.slot, Foo.instantiated)
        self.assertEqual(event.instance, foo)

        self.assertFalse(events)

        for key, value in values.iteritems():
            self.assertEqual(getattr(foo, key), value)

    def test_defaults(self):

        from cocktail.schema import Schema, SchemaObject, String, Integer

        class Foo(SchemaObject):
            bar = String(default = "Default bar")
            spam = Integer()

        events = EventLog()
        events.listen(
            Foo_changed = Foo.changed,
            Foo_changing = Foo.changing
        )

        foo = Foo()

        event = events.pop(0)

        self.assertEqual(event.slot, Foo.changing)
        self.assertEqual(event.member, Foo.bar)

        self.assertEqual(event.value, "Default bar")

        event = events.pop(0)
        self.assertEqual(event.slot, Foo.changed)
        self.assertEqual(event.member, Foo.bar)
        self.assertEqual(event.value, "Default bar")

        self.assertFalse(events)

        self.assertEqual(foo.bar, "Default bar")
        self.assertEqual(foo.spam, None)

    def test_per_class_defaults(self):

        from cocktail.schema import SchemaObject, String, DynamicDefault

        class Foo(SchemaObject):
            x = String(default = "foo")
            y = String()

        class Bar(Foo):
            default_x = "bar"
            default_y = DynamicDefault(lambda: "bar!")

        foo = Foo()
        assert foo.x == "foo"
        assert not foo.y

        bar = Bar()
        assert bar.x == "bar"
        assert bar.y == "bar!"

    def test_get_set(self):

        from cocktail.schema import Schema, SchemaObject, String, Integer

        class Foo(SchemaObject):
            bar = String()        
      
        events = EventLog()
        events.listen(
            Foo_changed = Foo.changed,
            Foo_changing = Foo.changing
        )

        foo = Foo()
        
        # First assignment
        foo.bar = "Spam!"

        event = events.pop(0)
        self.assertEqual(event.slot, Foo.changing)
        self.assertEqual(event.member, Foo.bar)
        self.assertEqual(event.value, "Spam!")
        self.assertEqual(event.previous_value, None)

        event = events.pop(0)
        self.assertEqual(event.slot, Foo.changed)
        self.assertEqual(event.member, Foo.bar)
        self.assertEqual(event.value, "Spam!")
        self.assertEqual(event.previous_value, None)

        self.assertFalse(events)

        self.assertEqual(foo.bar, "Spam!")

        # Second assignment
        foo.bar = None

        event = events.pop(0)
        self.assertEqual(event.slot, Foo.changing)
        self.assertEqual(event.member, Foo.bar)
        self.assertEqual(event.value, None)
        self.assertEqual(event.previous_value, "Spam!")

        event = events.pop(0)
        self.assertEqual(event.slot, Foo.changed)
        self.assertEqual(event.member, Foo.bar)
        self.assertEqual(event.value, None)
        self.assertEqual(event.previous_value, "Spam!")

        self.assertFalse(events)

        self.assertEqual(foo.bar, None)

    def test_alter_value_with_instance_event(self):

        from cocktail.schema import Schema, SchemaObject, String

        class Foo(SchemaObject):
            bar = String()
        
        foo = Foo()

        def alter_value(event):
            event.value += "!"

        foo.changing.append(alter_value)
        
        foo.bar = "Spam"        
        self.assertEqual(foo.bar, "Spam!")

    def test_alter_value_with_class_event(self):

        from cocktail.schema import Schema, SchemaObject, String

        class Foo(SchemaObject):
            bar = String()
        
        def alter_value(event):
            event.value += "!"

        Foo.changing.append(alter_value)

        foo = Foo()
        foo.bar = "Spam"        
        self.assertEqual(foo.bar, "Spam!")


class TranslationTestCase(TestCase):
    
    def test_declaration(self):

        from cocktail.schema import Schema, SchemaObject, String, Integer

        class Foo(SchemaObject):
            bar = String(translated = True)
            spam = Integer()

        self.assertTrue(Foo.translated)
        self.assertTrue(isinstance(Foo.translation, Schema))
        self.assertFalse(Foo.translation.translated)
        self.assertTrue(Foo.translation.translation_source is Foo)
        self.assertTrue(isinstance(Foo.translation.bar, String))
        self.assertTrue(Foo.translation.bar.translation_source is Foo.bar)
        self.assertTrue(Foo.translation.translation is None)
        self.assertRaises(AttributeError, getattr, Foo.translation, "spam")

    def test_inheritance(self):
        
        from cocktail.schema import SchemaObject, String, Integer

        class Foo(SchemaObject):
            foo_a = String(translated = True)
            foo_b = Integer()

        class Bar(Foo):
            bar_a = String()
            bar_b = Integer(translated = True)

        self.assertTrue(Foo.translation.translation_source is Foo)
        self.assertTrue(Foo.translation.foo_a.translation_source is Foo.foo_a)
        self.assertRaises(AttributeError, getattr, Foo.translation, "bar_a")
        self.assertRaises(AttributeError, getattr, Foo.translation, "bar_b")

        self.assertTrue(Bar.translation is not Foo.translation)
        self.assertTrue(issubclass(Bar.translation, Foo.translation))
        self.assertEqual(list(Bar.translation.bases), [Foo.translation])

        self.assertTrue(Bar.translation.translation_source is Bar)
        self.assertTrue(Foo.translation.foo_a.translation_source is Foo.foo_a)

    def test_get_set(self):
        pass

    def test_changing_translated_member_triggers_event(self):
    
        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            spam = String(translated = True)

        foo = Foo()
        foo.set("spam", u"green", "en")
        foo.set("spam", u"grün", "de")
        
        events = EventLog()
        events.listen(foo_changed = foo.changed)
    
        foo.set("spam", u"red", "en")
        foo.set("spam", u"rot", "de")

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == u"red"    
        assert event.previous_value == u"green"
        assert event.language == "en"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == u"rot"
        assert event.previous_value == u"grün"
        assert event.language == "de"

    def test_adding_translation_triggers_event(self):

        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            spam = String(translated = True)

        foo = Foo()

        events = EventLog()
        events.listen(foo_adding_translation = foo.adding_translation)

        foo.set("spam", u"green", "en")

        event = events.pop(0)
        assert event.slot is foo.adding_translation
        assert event.translation == foo.translations["en"]
        assert event.language == "en"

    def test_removing_translation_triggers_event(self):
        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            spam = String(translated = True)

        foo = Foo()
        foo.set("spam", u"green", "en")

        events = EventLog()
        events.listen(foo_removing_translation = foo.removing_translation)

        translation_object = foo.translations["en"]
        del foo.translations["en"]

        event = events.pop(0)
        assert event.slot is foo.removing_translation
        assert event.translation == translation_object
        assert event.language == "en"

    def test_changing_translation_notifies_owner(self):

        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            spam = String(translated = True)

        foo = Foo()
        foo.set("spam", u"green", "en")
        foo.set("spam", u"grün", "de")
        
        events = EventLog()
        events.listen(foo_changed = foo.changed)
    
        foo.translations["en"].spam = u"red"
        foo.translations["de"].spam = u"rot"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == u"red"    
        assert event.previous_value == u"green"
        assert event.language == "en"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == u"rot"
        assert event.previous_value == u"grün"
        assert event.language == "de"

    def test_adding_translation_notifies_owner(self):
        return

        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            spam = String(translated = True)
            bar = String(translated = True, default = "gray")

        foo = Foo()
        
        events = EventLog()
        events.listen(foo_changed = foo.changed)
    
        foo.set("spam", u"green", "en")
        foo.set("spam", u"grün", "de")

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == u"green"
        assert event.previous_value is None
        assert event.language == "en"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.bar
        assert event.value == u"gray"
        assert event.previous_value is None
        assert event.language == "en"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == u"grün"
        assert event.previous_value is None
        assert event.language == "de"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.bar
        assert event.value == u"gray"
        assert event.previous_value is None
        assert event.language == "de"


class CopyTestCase(TestCase):

    def test_copying_schema_object_class_produces_new_class(self):
        
        from cocktail.schema import Schema, SchemaObject

        class TestClass(SchemaObject):
            pass

        copy = TestClass.copy()
        assert copy is not TestClass
        assert isinstance(copy, type)
        assert issubclass(copy, SchemaObject)
        assert not issubclass(copy, type)

    def test_copying_schema_object_class_preserves_inheritance(self):

        from cocktail.schema import Schema, SchemaObject

        class BaseClass(SchemaObject):
            pass

        class DerivedClass(BaseClass):
            pass

        copy = DerivedClass.copy()
        assert issubclass(copy, BaseClass)

    def test_copying_schema_object_class_copies_members(self):
        
        from cocktail.schema import Schema, SchemaObject, String

        class TestClass(SchemaObject):            
            member1 = String(required = True)
            member2 = String(min = 3)

        copy = TestClass.copy()
        
        assert copy.members().keys() == TestClass.members().keys()
        
        assert copy.member1 is not TestClass.member1
        assert isinstance(copy.member1, String)
        assert copy.member1.copy_source is TestClass.member1
        assert copy.member1.original_member is TestClass.member1
        assert copy.member1.required

        assert copy.member2 is not TestClass.member2
        assert isinstance(copy.member2, String)
        assert copy.member2.copy_source is TestClass.member2
        assert copy.member2.original_member is TestClass.member2
        assert copy.member2.min == 3

