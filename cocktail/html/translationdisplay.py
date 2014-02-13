#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.schema import SchemaObject
from cocktail.html import Element


class TranslationDisplay(Element):

    value = None

    def _ready(self):

        Element._ready(self)

        if self.value is not None and self.member is not None:
            self.append(self.member.translate_value(self.value, self.language))

            if (
                self.language
                and isinstance(self.data, SchemaObject)
                and self.data.__class__.translated
            ):
                source_locale = self.data.get_source_locale(self.language)
                if self.language != source_locale:
                    self.add_class("inherited_translation")
                    self["title"] = \
                        self.get_translation_inheritance_remark(source_locale)
    
    def get_translation_inheritance_remark(self, source_locale):
        return translations(
            "cocktail.html.TranslationDisplay.translation_inheritance_remark",
            source_locale = source_locale
        )

