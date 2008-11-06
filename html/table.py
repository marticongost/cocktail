#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2007
"""
from cocktail.html.element import Element
from cocktail.html.datadisplay import (
    CollectionDisplay,
    NO_SELECTION, SINGLE_SELECTION, MULTIPLE_SELECTION
)
from cocktail.translations import translate
from cocktail.language import get_content_language, set_content_language
from cocktail.schema.expressions import (
    TranslationExpression,
    PositiveExpression,
    NegativeExpression
)
from cocktail.controllers.viewstate import view_state

class Table(Element, CollectionDisplay):
    
    tag = "table"
    ascending_order_image = "ascending.png"
    descending_order_image = "descending.png"
    base_image_url = None

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        CollectionDisplay.__init__(self)
        self.__column_display = {}
        self.__column_labels = {}

    def _build(self):

        self.head = Element("thead")
        self.append(self.head)

        self.head_row = Element("tr")
        self.head.append(self.head_row)

        self.body = Element("body")
        self.append(self.body)

    def _ready(self):
        
        self.add_resource("/cocktail/scripts/core.js")

        self.set_client_variable(
            "cocktail.NO_SELECTION", NO_SELECTION)
        self.set_client_variable(
            "cocktail.SINGLE_SELECTION", SINGLE_SELECTION)
        self.set_client_variable(
            "cocktail.MULTIPLE_SELECTION", MULTIPLE_SELECTION)
        
        self.set_client_param("selectionMode", self.selection_mode)

        self._fill_head()
        self._fill_body()

    def _fill_head(self):

        # Cache sorted columns
        if self.order:
            
            self.__sorted_columns = sorted_columns = {}
            
            for criteria in self.order:
                sign = criteria.__class__
                expr = criteria.operands[0]
                
                if isinstance(expr, TranslationExpression):
                    member = expr.operands[0].name
                    language = expr.operands[1].value
                else:
                    member = expr.name
                    language = None

                sorted_columns[(member, language)] = sign

        # Selection column
        if self.selection_mode != NO_SELECTION:
            selection_header = Element("th")
            selection_header.add_class("selection")
            self.head_row.append(selection_header)
        
        # Regular columns
        for column in self.displayed_members:
            if column.translated:
                for language in self.translations:
                    header = self.create_header(column, language)
                    self.head_row.append(header)
            else:
                header = self.create_header(column)
                self.head_row.append(header)
    
    def _fill_body(self):
        for i, item in enumerate(self.data):
            row = self.create_row(i, item)
            self.append(row)

    def create_row(self, index, item):
        row = Element("tr")
        row.add_class(index % 2 == 0 and "odd" or "even")
        
        if self.selection_mode != NO_SELECTION:
            row.append(self.create_selection_cell(item))
            
        for column in self.displayed_members:
            if self.translations and column.translated:
                current_content_language = get_content_language()
                for language in self.translations:
                    set_content_language(language)
                    cell = self.create_cell(item, column, language)
                    row.append(cell)
                set_content_language(current_content_language)
            else:
                cell = self.create_cell(item, column)
                row.append(cell)
        
        return row

    def create_selection_cell(self, item):

        selection_control = Element("input")
        selection_control["name"] = "selection"
        selection_control["id"] = "selection_" + str(item.id)
        selection_control["value"] = str(item.id)

        if self.selection_mode == SINGLE_SELECTION:
            selection_control["type"] = "radio"
        else:
            selection_control["type"] = "checkbox"

        selection_control["checked"] = self.is_selected(item)

        selection_cell = Element("td")
        selection_cell.add_class("selection")
        selection_cell.append(selection_control)
        return selection_cell

    def create_header(self, column, language = None):
        
        header = Element("th")
        self._init_cell(header, column, language)
        
        label = Element("span")
        label.add_class("label")
        label.append(self.get_member_label(column))
        header.append(label)

        # Sorting
        if self.get_member_sortable(column):
            label.tag = "a"
            sign = ""

            if self.order:
                current_direction = self.__sorted_columns.get(
                    (column.name, language)
                )

                if current_direction is not None:
                    header.add_class("sorted")

                    if current_direction is PositiveExpression:
                        header.add_class("ascending")
                        sign = "-"
                    elif current_direction is NegativeExpression:
                        header.add_class("descending")
 
            order_param = sign + column.name

            if language:
                order_param += "." + language

            label["href"] = "?" + view_state(order = order_param)

        # Translation label
        if language:
            translation_label = self.create_translation_label(language)
            header.append(translation_label)
                        
        return header
    
    def create_translation_label(self, language):
        label = Element("span")
        label.add_class("translation")
        label.append(u"(" + translate(language) + u")")
        return label

    def create_cell(self, item, column, language = None):
        cell = Element("td")

        if self.order \
        and (column.name, language) in self.__sorted_columns:
            cell.add_class("sorted")

        self._init_cell(cell, column, language)
        display = self.get_member_display(item, column)
        cell.append(display)
        return cell

    def _init_cell(self, cell, column, language = None):
        cell.add_class(column.name + "_column")

        if language:
            cell.add_class(language)

