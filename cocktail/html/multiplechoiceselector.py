#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.html.checklist import CheckList


class MultipleChoiceSelector(CheckList):

    def _build(self):
        
        CheckList._build(self)        
        self.add_resource("/cocktail/scripts/MultipleChoiceSelector.js")

        for key in ("accept button", "cancel button", "select button"):
            self.add_client_translation(
                "cocktail.html.MultipleChoiceSelector " + key
            )

