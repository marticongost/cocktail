#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema import IBAN
from cocktail.html import templates

TextBox = templates.get_class("cocktail.html.TextBox")


class IBANBox(TextBox):

    def _build(self):
        TextBox._build(self)
        self.add_resource("/cocktail/scripts/jquery.inputmask.js")
        self.add_resource("/cocktail/scripts/IBANBox.js")
        self.set_client_param("lengthByCountry", IBAN.length_by_country)

