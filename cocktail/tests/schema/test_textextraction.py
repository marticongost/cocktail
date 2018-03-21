#-*- coding: utf-8 -*-
u"""

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
        obj1.field1 = u"John"
        obj1.field2 = u"Johnson"
        obj1.set("m3", u"Cat", "en")
        obj1.set("m3", u"Gato", "es")

        self.assert_text(obj1, [None], u"John Johnson")

        obj2 = Model1()
        obj2.field1 = u"James"
        obj2.field2 = u"Jameson"
        obj2.set("m3", u"Dog", "en")
        obj2.set("m3", u"Perro", "es")

        self.assert_text(obj2, [None], u"James Jameson")

    def test_can_extract_text_from_translated_members(self):

        from cocktail import schema

        class Model1(schema.SchemaObject):
            field1 = schema.String()
            field2 = schema.String()
            m3 = schema.String(translated = True)

        obj1 = Model1()
        obj1.field1 = u"John"
        obj1.field2 = u"Johnson"
        obj1.set("m3", u"Cat", "en")
        obj1.set("m3", u"Gato", "es")

        self.assert_text(obj1, ["en"], u"Cat")
        self.assert_text(obj1, ["es"], u"Gato")
        self.assert_text(obj1, ["es", "en"], u"Gato Cat")

        obj2 = Model1()
        obj2.field1 = u"James"
        obj2.field2 = u"Jameson"
        obj2.set("m3", u"Dog", "en")
        obj2.set("m3", u"Perro", "es")

        self.assert_text(obj2, ["en"], u"Dog")
        self.assert_text(obj2, ["es"], u"Perro")
        self.assert_text(obj2, ["en", "es"], u"Dog Perro")

    def test_can_extract_text_including_translated_and_untranslated_members(self):

        from cocktail import schema

        class Model1(schema.SchemaObject):
            field1 = schema.String()
            field2 = schema.String()
            m3 = schema.String(translated = True)

        obj1 = Model1()
        obj1.field1 = u"John"
        obj1.field2 = u"Johnson"
        obj1.set("m3", u"Cat", "en")
        obj1.set("m3", u"Gato", "es")

        self.assert_text(obj1, [None, "en"], u"John Johnson Cat")
        self.assert_text(obj1, ["es", None], u"Gato John Johnson")
        self.assert_text(obj1, [None, "es", "en"], u"John Johnson Gato Cat")

    def test_extraction_languages_default_to_object_translations(self):

        from cocktail import schema
        from cocktail.translations import translations

        class Model(schema.SchemaObject):
            field1 = schema.String()
            field2 = schema.String(translated = True)
            field3 = schema.String(enumeration = ["icecream", "pie"])

        translations.define(
            Model.full_name + ".members.field3.values.icecream",
            es = u"Helado",
            en = u"Ice cream"
        )

        translations.define(
            Model.full_name + ".members.field3.values.pie",
            es = u"Pastel",
            en = u"Pie"
        )

        obj = Model()
        obj.field1 = "Foobar"
        obj.set("field2", u"Dog", "en")
        obj.set("field2", u"Perro", "es")
        obj.field3 = "pie"

        assert (
            set(obj.get_searchable_text().split())
            == {u"Foobar", u"Dog", u"Perro", u"Pastel", u"Pie"}
        )

    def test_enumerations_produce_translated_text(self):

        from cocktail import schema
        from cocktail.translations import translations

        class Model1(schema.SchemaObject):
            field1 = schema.String(enumeration = ["cat", "dog"])

        translations.define(
            Model1.full_name + ".members.field1.values.cat",
            es = u"Gato",
            en = u"Cat"
        )

        translations.define(
            Model1.full_name + ".members.field1.values.dog",
            es = u"Perro",
            en = u"Dog"
        )

        obj1 = Model1()

        obj1.field1 = "cat"
        self.assert_text(obj1, ["en"], u"Cat")
        self.assert_text(obj1, ["es"], u"Gato")
        self.assert_text(obj1, [None], set())

        obj1.field1 = "dog"
        self.assert_text(obj1, ["en"], u"Dog")
        self.assert_text(obj1, ["es"], u"Perro")
        self.assert_text(obj1, [None], u"")

        Model1.field1.translatable_enumeration = False
        self.assert_text(obj1, ["en"], u"")
        self.assert_text(obj1, ["es"], u"")
        self.assert_text(obj1, [None], u"dog")

    def test_can_exclude_members_from_text_extraction(self):

        from cocktail import schema

        class Model1(schema.SchemaObject):
            field1 = schema.String()
            field2 = schema.String(text_search = False)

        obj1 = Model1()
        obj1.field1 = u"John"
        obj1.field2 = u"Johnson"

        self.assert_text(obj1, [None], u"John")

    def test_can_recurse_into_references(self):

        from cocktail import schema

        class Model(schema.SchemaObject):
            text = schema.String()
            translated_text = schema.String()
            ref = schema.Reference()

        Model.ref.type = Model

        obj = Model()
        obj.text = u"Foo"
        obj.ref = Model()
        obj.ref.text = u"Bar"
        obj.ref.ref = Model()
        obj.ref.set("translated_text", u"Hola", "es")
        obj.ref.ref.text = u"Spam"
        obj.ref.ref.set("translated_text", u"Hello", "en")

        self.assert_text(obj, [None, "es", "en"], u"Foo")

        Model.ref.text_search = True

        self.assert_text(obj, [None, "es", "en"], u"Foo Bar Spam Hola Hello")
        self.assert_text(obj.ref, [None, "es", "en"], u"Bar Spam Hola Hello")
        self.assert_text(obj.ref.ref, [None, "es", "en"], u"Spam Hello")

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

        self.assert_text(obj, [None], u"Foo Bar")
        self.assert_text(obj.ref, [None], u"Foo Bar")

    def test_can_recurse_into_collections(self):

        from cocktail import schema

        class Model(schema.SchemaObject):
            text = schema.String()
            translated_text = schema.String()
            items = schema.Collection()

        Model.items.items = schema.Reference(type = Model)

        obj = Model()
        obj.text = u"Foo"
        obj.items.append(Model())
        obj.items[0].text = u"Bar"
        obj.items[0].set("translated_text", u"Hola", "es")
        obj.items.append(Model())
        obj.items[1].text = u"Spam"
        obj.items[1].set("translated_text", u"Hello", "en")

        self.assert_text(obj, [None, "es", "en"], u"Foo")

        Model.items.text_search = True
        self.assert_text(obj, [None, "es", "en"], u"Foo Bar Spam Hola Hello")

