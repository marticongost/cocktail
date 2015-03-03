#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail.html.textbox import TextBox


class MaskedInputBox(TextBox):

    input_mask = None

    def _ready(self):

        if self.member.input_mask:
            self.input_mask = self.member.input_mask

        if self.input_mask:
            self.add_resource("/cocktail/scripts/jquery.inputmask.js")
            self.set_client_param("inputMask", self.input_mask)
            self.add_client_code("jQuery(this).inputmask(this.inputMask)")

