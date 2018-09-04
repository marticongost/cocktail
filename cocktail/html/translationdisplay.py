#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.schema import SchemaObject
from cocktail.html import Element


class TranslationDisplay(Element):

    empty_label = u"∅"

    def _ready(self):

        Element._ready(self)

        if self.member is not None:
            label = self.member.translate_value(self.value, self.language)
            if not label:
                label = self.get_empty_label()
                self.add_class("empty")
            self.append(label)

            if (
                self.value is not None
                and self.language
                and self.member.translated
                and isinstance(self.data, SchemaObject)
                and self.data.__class__.translated
            ):
                source_locale = self.data.get_source_locale(self.language)
                if source_locale and self.language != source_locale:
                    self.add_class("inherited_translation")
                    self["title"] = \
                        self.get_translation_inheritance_remark(source_locale)

    def get_empty_label(self):
        return self.empty_label

    def get_translation_inheritance_remark(self, source_locale):
        return translations(
            "cocktail.html.TranslationDisplay.translation_inheritance_remark",
            source_locale = source_locale
        )

