#-*- coding: utf-8 -*-
"""

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
            "name", "schema", "source_member", "translated", "translation",
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

        for key, value in values.items():
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

    def test_can_delay_default_assignment(self):

        from cocktail.schema import SchemaObject, String, undefined

        class Foo(SchemaObject):
            spam = String(default = "foo")

        foo = Foo(spam = undefined)
        assert not hasattr(foo, "_spam")
        assert foo.spam == "foo"
        assert hasattr(foo, "_spam")

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
        foo.set("spam", "green", "en")
        foo.set("spam", "grün", "de")

        events = EventLog()
        events.listen(foo_changed = foo.changed)

        foo.set("spam", "red", "en")
        foo.set("spam", "rot", "de")

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == "red"
        assert event.previous_value == "green"
        assert event.language == "en"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == "rot"
        assert event.previous_value == "grün"
        assert event.language == "de"

    def test_adding_translation_triggers_event(self):

        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            spam = String(translated = True)

        foo = Foo()

        events = EventLog()
        events.listen(foo_adding_translation = foo.adding_translation)

        foo.set("spam", "green", "en")

        event = events.pop(0)
        assert event.slot is foo.adding_translation
        assert event.translation == foo.translations["en"]
        assert event.language == "en"

    def test_removing_translation_triggers_event(self):
        from cocktail.schema import SchemaObject, String

        class Foo(SchemaObject):
            spam = String(translated = True)

        foo = Foo()
        foo.set("spam", "green", "en")

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
        foo.set("spam", "green", "en")
        foo.set("spam", "grün", "de")

        events = EventLog()
        events.listen(foo_changed = foo.changed)

        foo.translations["en"].spam = "red"
        foo.translations["de"].spam = "rot"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == "red"
        assert event.previous_value == "green"
        assert event.language == "en"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == "rot"
        assert event.previous_value == "grün"
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

        foo.set("spam", "green", "en")
        foo.set("spam", "grün", "de")

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == "green"
        assert event.previous_value is None
        assert event.language == "en"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.bar
        assert event.value == "gray"
        assert event.previous_value is None
        assert event.language == "en"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.spam
        assert event.value == "grün"
        assert event.previous_value is None
        assert event.language == "de"

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is Foo.bar
        assert event.value == "gray"
        assert event.previous_value is None
        assert event.language == "de"


class TranslationInheritanceTestCase(TestCase):

    def test_translations_can_be_inherited(self):

        from cocktail.translations import (
            translations,
            fallback_languages_context
        )
        from cocktail import schema

        class TestObject(schema.SchemaObject):
            test_field = schema.String(
                translated = True
            )

        obj = TestObject()

        with fallback_languages_context({
            "en-CA": ["en"],
            "fr-CA": ["fr", "en-CA"]
        }):
            obj.set("test_field", "I'm full", "en")
            assert obj.get("test_field", "en-CA") == "I'm full"
            assert obj.get("test_field", "fr-CA") == "I'm full"

            obj.set("test_field", "j'ai trop mangé", "fr")
            assert obj.get("test_field", "fr-CA") == "j'ai trop mangé"

            obj.set("test_field", "je suis plein", "fr-CA")
            assert obj.get("test_field", "fr-CA") == "je suis plein"

            del obj.translations["fr-CA"]
            assert obj.get("test_field", "fr-CA") == "j'ai trop mangé"

            del obj.translations["fr"]
            assert obj.get("test_field", "fr-CA") == "I'm full"

    def test_new_translations_inherit_values(self):

        from cocktail.translations import (
            translations,
            fallback_languages_context
        )
        from cocktail import schema

        class TestObject(schema.SchemaObject):
            test_field = schema.String(
                translated = True
            )

        obj = TestObject()
        obj.set("test_field", "I'm full", "en")
        obj.set("test_field", "j'ai trop mangé", "fr")

        with fallback_languages_context({
            "en-CA": ["en"],
            "fr-CA": ["fr", "en-CA"]
        }):
            obj.new_translation("en-CA")
            assert obj.get("test_field", "en-CA") == "I'm full"

            obj.new_translation("fr-CA")
            assert obj.get("test_field", "fr-CA") == "j'ai trop mangé"

    def test_changing_the_language_chain_affects_translation_inheritance(self):

        from cocktail.translations import (
            translations,
            fallback_languages_context
        )
        from cocktail import schema

        class TestObject(schema.SchemaObject):
            test_field = schema.String(
                translated = True
            )

        obj = TestObject()
        obj.set("test_field", "I'm full", "en")
        obj.set("test_field", "j'ai trop mangé", "fr")

        with fallback_languages_context({
            "en-CA": ["en"],
            "fr-CA": ["fr", "en-CA"]
        }):
            assert obj.get("test_field", "fr-CA") == "j'ai trop mangé"

        with fallback_languages_context({
            "en-CA": ["en"],
            "fr-CA": ["en-CA"]
        }):
            assert obj.get("test_field", "fr-CA") == "I'm full"


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

        assert list(copy.members().keys()) == list(TestClass.members().keys())

        assert copy.member1 is not TestClass.member1
        assert isinstance(copy.member1, String)
        assert copy.member1.source_member is TestClass.member1
        assert copy.member1.original_member is TestClass.member1
        assert copy.member1.required

        assert copy.member2 is not TestClass.member2
        assert isinstance(copy.member2, String)
        assert copy.member2.source_member is TestClass.member2
        assert copy.member2.original_member is TestClass.member2
        assert copy.member2.min == 3


class CollectionChangeEventsTestCase(TestCase):

    def test_reordering_collection_fires_change_events(self):

        from cocktail.tests.utils import EventLog
        from cocktail.schema import SchemaObject, Collection

        class TestClass(SchemaObject):
            member1 = Collection()

        foo = TestClass()
        foo.member1 = [1, 2]

        events = EventLog()
        events.listen(foo_changed = foo.changed)

        foo.member1 = [2, 1]

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is TestClass.member1
        assert event.value == [2, 1]

    def test_appending_fires_change_events(self):

        from cocktail.tests.utils import EventLog
        from cocktail.schema import SchemaObject, Collection

        class TestClass(SchemaObject):
            member1 = Collection()

        foo = TestClass()
        foo.member1 = [1, 2]

        events = EventLog()
        events.listen(foo_changed = foo.changed)

        foo.member1.append(3)

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is TestClass.member1
        assert event.value == [1, 2, 3]

    def test_removing_fires_change_events(self):

        from cocktail.tests.utils import EventLog
        from cocktail.schema import SchemaObject, Collection

        class TestClass(SchemaObject):
            member1 = Collection()

        foo = TestClass()
        foo.member1 = [1, 2, 3]

        events = EventLog()
        events.listen(foo_changed = foo.changed)

        foo.member1.remove(2)

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is TestClass.member1
        assert event.value == [1, 3]

    def test_inserting_fires_change_events(self):

        from cocktail.tests.utils import EventLog
        from cocktail.schema import SchemaObject, Collection

        class TestClass(SchemaObject):
            member1 = Collection()

        foo = TestClass()
        foo.member1 = [1, 2, 3]

        events = EventLog()
        events.listen(foo_changed = foo.changed)

        foo.member1.insert(1, 0)

        event = events.pop(0)
        assert event.slot is foo.changed
        assert event.member is TestClass.member1
        assert event.value == [1, 0, 2, 3]

