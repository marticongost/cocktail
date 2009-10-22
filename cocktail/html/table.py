#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2007
"""
from cocktail.html import templates
from cocktail.html.element import Element
from cocktail.html.selectable import selectable
from cocktail.html.datadisplay import (
    CollectionDisplay,
    NO_SELECTION, SINGLE_SELECTION, MULTIPLE_SELECTION
)
from cocktail.translations import translations
from cocktail.language import get_content_language, set_content_language
from cocktail.schema import Collection, get
from cocktail.schema.expressions import (
    TranslationExpression,
    PositiveExpression,
    NegativeExpression
)
from cocktail.controllers.viewstate import view_state


class Table(Element, CollectionDisplay):
    
    tag = "table"
    sortable = False
    ascending_order_image = "ascending.png"
    descending_order_image = "descending.png"
    base_image_url = None
    selection_parameter = "selection"
    nested_list_max_length = 5
    translated_values = True
    persistence_prefix = None
    entry_selector = "tbody tr"
    checkbox_selector = "td.selection input"
    resizable_rows_selector = "tbody tr"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        CollectionDisplay.__init__(self)
        self.__column_display = {}
        self.__column_labels = {}
        self.set_member_type_display(Collection, self.display_collection)
        self.add_class("resizable")

    def _build(self):

        self.head = Element("thead")
        self.append(self.head)

        self.head_row = Element("tr")
        self.head.append(self.head_row)

        self.body = Element("body")
        self.append(self.body)

    def _ready(self):
                
        Element._ready(self)
        self.add_resource("/cocktail/scripts/jquery.cookie.js")
        self.add_resource("/cocktail/scripts/jquery.tableresizer.js")

        selectable(
            self,
            mode = self.selection_mode,
            entry_selector = self.entry_selector,
            checkbox_selector = self.checkbox_selector
        )

        self.set_client_param(
            "resizableRowsSelector",
            self.resizable_rows_selector
        )

        self.set_client_param("persistencePrefix", self.persistence_prefix)

        if self.grouping:
            self.set_member_displayed(self.grouping.member, False)
            self._grouping_member_translation = \
                u"(" + translations(self.grouping.member) + u")"
            self._remove_grouping_translation = \
                translations("sitebasis.views.ContentTable remove grouping")

        self._fill_head()
        self._fill_body()

    def _fill_head(self):

        # Cache sorted columns
        if self.order:
            
            self._sorted_columns = sorted_columns = {}
            
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

        if self.grouping:
            undefined = object()
            current_group = undefined        
            get_group = self.grouping.get_grouping_value
        else:
            get_group = None

        for i, item in enumerate(self.data):

            if get_group:
                group = get_group(item)
                if group != current_group:
                    group_row = self.create_group_row(group)
                    self.append(group_row)
                    current_group = group

            row = self.create_row(i, item)
            self.append(row)
            self._row_added(i, item, row)

    def _row_added(self, index, item, row):
        pass

    def create_group_row(self, group):
        
        row = Element("tr")
        row.add_class("group")
        
        cell = Element("td", colspan = "0", children = [
            Element("span",
                class_name = "grouping_value",
                children = [
                    self.grouping.translate_grouping_value(group)
                    or self.translate_value(
                        self.data,
                        self.grouping.member,
                        group
                    )
                ]
            ),
            Element("span",
                class_name = "grouping_member",
                children = [self._grouping_member_translation]
            ),
            Element("a",
                href = u"?" + view_state(grouping = "", page = 0),
                class_name = "remove_grouping",
                children = [self._remove_grouping_translation]
            )
        ])
        row.append(cell)
        
        return row

    def create_row(self, index, item):
        row = Element("tr")
        row.add_class(index % 2 == 0 and "odd" or "even")
        
        if self.selection_mode != NO_SELECTION:
            row.append(self.create_selection_cell(item))

        if self.schema.primary_member:
            row["id"] = item.id
                    
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

    def get_item_id(self, item):
        pm = self.schema.primary_member
        if pm is None:
            raise ValueError(
                "Selectable tables must have a schema with a primary member "
                "defined or override their get_item_id() method"
            )
        return get(item, pm)

    def create_selection_cell(self, item):        
        selection_cell = Element("td")
        selection_cell.add_class("selection")
        selection_cell.append(self.create_selection_control(item))
        return selection_cell

    def create_selection_control(self, item):

        id = self.get_item_id(item)

        selection_control = Element("input")
        selection_control["name"] = self.selection_parameter
        selection_control["id"] = "selection_" + str(id)
        selection_control["value"] = id
        selection_control["autocomplete"] = "off"

        if self.selection_mode == SINGLE_SELECTION:
            selection_control["type"] = "radio"
        else:
            selection_control["type"] = "checkbox"

        selection_control["checked"] = self.is_selected(item)

        return selection_control

    def create_header(self, column, language = None):
        
        header = Element("th")
        self._init_cell(header, column, language)
        
        header.label = Element("span")
        header.label.add_class("label")
        header.label.append(self.get_member_label(column))
        header.append(header.label)
        
        # Translation label
        if language:
            header.translation_label = self.create_translation_label(language)
            header.append(header.translation_label)
        
        self.add_header_ui(header, column, language)
        return header       

    def create_translation_label(self, language):
        label = Element("span")
        label.add_class("translation")
        label.append(u"(" + translations(language) + u")")
        return label

    def add_header_ui(self, header, column, language):

        # Sorting
        if self.get_member_sortable(column):
            header.label.tag = "a"
            sign = ""

            if self.order:
                current_direction = self._sorted_columns.get(
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

            header.label["href"] = "?" + view_state(
                order = order_param,
                page = 0
            )

    def create_cell(self, item, column, language = None):
        cell = Element("td")

        if self.order \
        and (column.name, language) in self._sorted_columns:
            cell.add_class("sorted")

        self._init_cell(cell, column, language)
        display = self.get_member_display(item, column)
        cell.append(display)
        return cell

    def _init_cell(self, cell, column, language = None):
        cell.add_class(column.name + "_column")

        if language:
            cell.add_class(language)

    def display_collection(self, obj, member):
        list = templates.new("cocktail.html.List")
        list.items = self.get_member_value(obj, member)
        list.max_length = self.nested_list_max_length
        return list

