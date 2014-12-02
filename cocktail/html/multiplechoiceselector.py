#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.html.checklist import CheckList
from cocktail.html.modalselector import modal_selector


class MultipleChoiceSelector(CheckList):

    def _build(self):
        CheckList._build(self)        
        modal_selector(self)      

