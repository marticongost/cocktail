#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations.strings import DATE_STYLE_ABBR
from cocktail import schema
from cocktail.html.valuedisplay import ValueDisplay


class RelativeTimeDisplay(ValueDisplay):

    translation_options = {
        "include_seconds": False,
        "style": DATE_STYLE_ABBR,
        "relative": True
    }

    title_translation_options = {}

    def _ready(self):

        if (
            isinstance(self.member, schema.Date)
            and self.translation_options
            and "include_seconds" in self.translation_options
        ):
            self.translation_options = self.translation_options.copy()
            del self.translation_options["include_seconds"]

        ValueDisplay._ready(self)

        if self.member and self.value:
            self["title"] = self.member.translate_value(
                self.value,
                **self.title_translation_options
            )

