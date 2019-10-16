#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase


class TextExtractionTestCase(TestCase):

    def assert_text(self, obj, languages, expected_text):

        if not isinstance(expected_text, set):
            expected_text = set(expected_text.split())

        text = set(obj.get_searchable_text(languages).split())
        assert text == expected_text

    def test_can_extract_text_from_non_translated_members(self):

        from cocktail import schema

        class Model1(schema.SchemaObject):
            field1 = schema.String()
            field2 = schema.String()
            m3 = schema.String(translated = True)

        obj1 = Model1()
        obj1.field1 = "John"
        obj1.field2 = "Johnson"
        obj1.set("m3", "Cat", "en")
        obj1.set("m3", "Gato", "es")

        self.assert_text(obj1, [None], "John Johnson")

        obj2 = Model1()
        obj2.field1 = "James"
        obj2.field2 = "Jameson"
        obj2.set("m3", "Dog", "en")
        obj2.set("m3", "Perro", "es")

        self.assert_text(obj2, [None], "James Jameson")

    def test_can_extract_text_from_translated_members(self):

        from cocktail import schema

        class Model1(schema.SchemaObject):
            field1 = schema.String()
            field2 = schema.String()
            m3 = schema.String(translated = True)

        obj1 = Model1()
        obj1.field1 = "John"
        obj1.field2 = "Johnson"
        obj1.set("m3", "Cat", "en")
        obj1.set("m3", "Gato", "es")

        self.assert_text(obj1, ["en"], "Cat")
        self.assert_text(obj1, ["es"], "Gato")
        self.assert_text(obj1, ["es", "en"], "Gato Cat")

        obj2 = Model1()
        obj2.field1 = "James"
        obj2.field2 = "Jameson"
        obj2.set("m3", "Dog", "en")
        obj2.set("m3", "Perro", "es")

        self.assert_text(obj2, ["en"], "Dog")
        self.assert_text(obj2, ["es"], "Perro")
        self.assert_text(obj2, ["en", "es"], "Dog Perro")

    def test_can_extract_text_including_translated_and_untranslated_members(self):

        from cocktail import schema

        class Model1(schema.SchemaObject):
            field1 = schema.String()
            field2 = schema.String()
            m3 = schema.String(translated = True)

        obj1 = Model1()
        obj1.field1 = "John"
        obj1.field2 = "Johnson"
        obj1.set("m3", "Cat", "en")
        obj1.set("m3", "Gato", "es")

        self.assert_text(obj1, [None, "en"], "John Johnson Cat")
        self.assert_text(obj1, ["es", None], "Gato John Johnson")
        self.assert_text(obj1, [None, "es", "en"], "John Johnson Gato Cat")

    def test_extraction_languages_default_to_object_translations(self):

        from cocktail import schema
        from cocktail.translations import translations

        class Model(schema.SchemaObject):
            field1 = schema.String()
            field2 = schema.String(translated = True)
            field3 = schema.String(enumeration = ["icecream", "pie"])

        translations.define(
            Model.full_name + ".members.field3.values.icecream",
            es = "Helado",
            en = "Ice cream"
        )

        translations.define(
            Model.full_name + ".members.field3.values.pie",
            es = "Pastel",
            en = "Pie"
        )

        obj = Model()
        obj.field1 = "Foobar"
        obj.set("field2", "Dog", "en")
        obj.set("field2", "Perro", "es")
        obj.field3 = "pie"

        assert (
            set(obj.get_searchable_text().split())
            == {"Foobar", "Dog", "Perro", "Pastel", "Pie"}
        )

    def test_enumerations_produce_translated_text(self):

        from cocktail import schema
        from cocktail.translations import translations

        class Model1(schema.SchemaObject):
            field1 = schema.String(enumeration = ["cat", "dog"])

        translations.define(
            Model1.full_name + ".members.field1.values.cat",
            es = "Gato",
            en = "Cat"
        )

        translations.define(
            Model1.full_name + ".members.field1.values.dog",
            es = "Perro",
            en = "Dog"
        )

        obj1 = Model1()

        obj1.field1 = "cat"
        self.assert_text(obj1, ["en"], "Cat")
        self.assert_text(obj1, ["es"], "Gato")
        self.assert_text(obj1, [None], set())

        obj1.field1 = "dog"
        self.assert_text(obj1, ["en"], "Dog")
        self.assert_text(obj1, ["es"], "Perro")
        self.assert_text(obj1, [None], "")

        Model1.field1.translatable_enumeration = False
        self.assert_text(obj1, ["en"], "")
        self.assert_text(obj1, ["es"], "")
        self.assert_text(obj1, [None], "dog")

    def test_can_exclude_members_from_text_extraction(self):

        from cocktail import schema

        class Model1(schema.SchemaObject):
            field1 = schema.String()
            field2 = schema.String(text_search = False)

        obj1 = Model1()
        obj1.field1 = "John"
        obj1.field2 = "Johnson"

        self.assert_text(obj1, [None], "John")

    def test_can_recurse_into_references(self):

        from cocktail import schema

        class Model(schema.SchemaObject):
            text = schema.String()
            translated_text = schema.String()
            ref = schema.Reference()

        Model.ref.type = Model

        obj = Model()
        obj.text = "Foo"
        obj.ref = Model()
        obj.ref.text = "Bar"
        obj.ref.ref = Model()
        obj.ref.set("translated_text", "Hola", "es")
        obj.ref.ref.text = "Spam"
        obj.ref.ref.set("translated_text", "Hello", "en")

        self.assert_text(obj, [None, "es", "en"], "Foo")

        Model.ref.text_search = True

        self.assert_text(obj, [None, "es", "en"], "Foo Bar Spam Hola Hello")
        self.assert_text(obj.ref, [None, "es", "en"], "Bar Spam Hola Hello")
        self.assert_text(obj.ref.ref, [None, "es", "en"], "Spam Hello")

    def test_extraction_avoids_reference_cycles(self):

        from cocktail import schema

        class Model(schema.SchemaObject):
            text = schema.String()
            ref = schema.Reference(text_search = True)

        Model.ref.type = Model

        obj = Model()
        obj.text = "Foo"
        obj.ref = Model()
        obj.ref.text = "Bar"
        obj.ref.ref = obj

        self.assert_text(obj, [None], "Foo Bar")
        self.assert_text(obj.ref, [None], "Foo Bar")

    def test_can_recurse_into_collections(self):

        from cocktail import schema

        class Model(schema.SchemaObject):
            text = schema.String()
            translated_text = schema.String()
            items = schema.Collection()

        Model.items.items = schema.Reference(type = Model)

        obj = Model()
        obj.text = "Foo"
        obj.items.append(Model())
        obj.items[0].text = "Bar"
        obj.items[0].set("translated_text", "Hola", "es")
        obj.items.append(Model())
        obj.items[1].text = "Spam"
        obj.items[1].set("translated_text", "Hello", "en")

        self.assert_text(obj, [None, "es", "en"], "Foo")

        Model.items.text_search = True
        self.assert_text(obj, [None, "es", "en"], "Foo Bar Spam Hola Hello")

