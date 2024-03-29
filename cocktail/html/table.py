#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2007
"""

from cocktail.html.element import Element
from cocktail.html.selectable import selectable
from cocktail.html.datadisplay import (
    CollectionDisplay,
    NO_SELECTION, SINGLE_SELECTION, MULTIPLE_SELECTION
)
from cocktail.translations import (
    translations,
    directionality,
    get_language,
    language_context,
    translate_locale
)
from cocktail.schema import Collection, Mapping, get
from cocktail.schema.expressions import (
    TranslationExpression,
    PositiveExpression,
    NegativeExpression
)
from cocktail.controllers import get_request_query


class Table(Element, CollectionDisplay):

    tag = "table"
    sortable = False
    show_language_headers = True
    grouped = True
    column_groups_displayed = False
    ascending_order_image = "ascending.png"
    descending_order_image = "descending.png"
    base_image_url = None
    selection_parameter = "selection"
    persistence_prefix = None
    entry_selector = "tbody tr"
    checkbox_selector = ".row_selection_control"
    use_separate_selection_column = True
    exclusive_selection = True
    __split_rows = None

    def __init__(self, *args, **kwargs):
        CollectionDisplay.__init__(self)
        self.__column_display = {}
        self.__column_labels = {}
        self.__split_rows = {}
        self.__split_row_values = {}
        self.__split_row_iterators = {}
        Element.__init__(self, *args, **kwargs)

    def _build(self):

        self.head = Element("thead")
        self.append(self.head)

        self.column_groups_row = Element("tr")
        self.head.append(self.column_groups_row)

        self.head_row = Element("tr")
        self.head.append(self.head_row)

        self.body = Element("tbody")
        self.append(self.body)

    def _ready(self):

        Element._ready(self)

        selectable(
            self,
            mode = self.selection_mode,
            entry_selector = self.entry_selector,
            checkbox_selector = self.checkbox_selector,
            exclusive = self.exclusive_selection
        )

        self.set_client_param("persistencePrefix", self.persistence_prefix)

        if self.grouping:
            self.set_member_displayed(self.grouping.member, False)
            self._grouping_member_translation = \
                "(" + translations(self.grouping.member) + ")"
            self._remove_grouping_translation = \
                translations("cocktail.html.Table.remove_grouping")

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
        if (
            self.selection_mode != NO_SELECTION
            and self.use_separate_selection_column
        ):
            selection_header = Element("th")
            selection_header.add_class("selection")
            self.head_row.append(selection_header)

        # Column groups
        if not self.grouped or not self.column_groups_displayed:
            self.column_groups_row.visible = False

        # Regular columns
        if self.grouped:
            self.columns_by_group = list(self.displayed_members_by_group)
        else:
            self.columns_by_group = [(None, list(self.displayed_members))]

        for group, columns in self.columns_by_group:

            if self.grouped and self.column_groups_displayed:
                self.column_groups_row.append(
                    self.create_column_group_header(group, columns)
                )

            for column in columns:
                if column.translated:
                    for language in self.translations or (get_language(),):
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
                    self.body.append(group_row)
                    current_group = group

            row = self.create_row(i, item)
            self.body.append(row)
            self._add_split_rows(item, row)
            self._row_added(i, item, row)

    def _add_split_rows(self, item, row):

        if not self.__split_rows:
            return

        row_span = 1
        end = False

        while not end:
            extra_row = Element("tr")
            has_content = False

            for group, columns in self.columns_by_group:
                for column in columns:
                    key = column.name
                    iterator = self.__split_row_iterators.get(key)
                    cell = None

                    if iterator is not None:
                        try:
                            self.__split_row_values[key] = next(iterator)
                        except StopIteration:
                            end = True
                        else:
                            cell = self.create_cell(item, column)
                            has_content = True

                    if cell is not None:
                        extra_row.append(cell)

            if has_content:
                self.append(extra_row)
                row_span += 1

        for cell in row.children:
            if cell.member is None \
            or cell.member.name not in self.__split_rows:
                cell["rowspan"] = row_span

    def _row_added(self, index, item, row):
        pass

    def create_group_row(self, group):

        row = Element("tr")
        row.add_class("group")

        cell = Element("td",
            colspan = len(self.head_row.children),
            children = [
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
                    href = "?" + get_request_query(
                        grouping = "",
                        page = 0
                    ).escape(),
                    class_name = "remove_grouping",
                    children = [self._remove_grouping_translation]
                )
            ]
        )
        row.append(cell)

        return row

    def create_row(self, index, item):

        self.__split_row_iterators.clear()
        self.__split_row_values.clear()

        row = Element("tr")
        row.add_class(index % 2 == 0 and "odd" or "even")

        if (
            self.selection_mode != NO_SELECTION
            and self.use_separate_selection_column
        ):
            row.append(self.create_selection_cell(item))

        if self.schema.primary_member:
            row["id"] = item.id

        for group, columns in self.columns_by_group:
            for column in columns:
                if self.translations and column.translated:
                    for language in self.translations:
                        with language_context(language):
                            cell = self.create_cell(item, column, language)
                            row.append(cell)
                else:
                    key = column.name
                    sequence_factory = self.__split_rows.get(key)

                    if sequence_factory is not None:
                        iterator = iter(sequence_factory(item))
                        self.__split_row_iterators[key] = iterator

                        try:
                            value = next(iterator)
                        except StopIteration:
                            value = None

                        self.__split_row_values[key] = value

                    cell = self.create_cell(item, column)
                    row.append(cell)

        if (
            self.selection_mode != NO_SELECTION
            and not self.use_separate_selection_column
        ):
            row.children[0].insert(0, self.create_selection_control(item))

        return row

    def split_rows(self, member, sequence_factory, parent = None):

        if parent is not None:
            raise RuntimeError("Nesting split rows not implemented yet")

        if not isinstance(member, str):
            member = member.name

        self.__split_rows[member] = sequence_factory
        self.set_member_expression(
            member,
            lambda item: self.__split_row_values[member]
        )

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
        selection_control.add_class("row_selection_control")

        if self.selection_mode == SINGLE_SELECTION:
            selection_control["type"] = "radio"
        else:
            selection_control["type"] = "checkbox"

        selection_control["checked"] = self.is_selected(item)

        return selection_control

    def create_column_group_header(self, group, columns):
        header = Element("th")
        header.add_class("column_group")
        header["colspan"] = len(columns)
        header.append(self.get_column_group_header_label(group, columns))
        return header

    def get_column_group_header_label(self, group, columns):
        if group and self.schema and self.schema.name:
            return translations("%s.%s_group" % (self.schema.name, group))
        else:
            return ""

    def create_header(self, column, language = None):

        header = Element("th")
        self._init_cell(header, column, language)

        header.label = Element("span")
        header.label.add_class("label")
        header.label.append(self.get_member_label(column))
        header.append(header.label)

        # Translation label
        if self.show_language_headers and language:
            header.translation_label = self.create_translation_label(language)
            header.append(header.translation_label)

        self.add_header_ui(header, column, language)
        return header

    def create_translation_label(self, language):
        label = Element("span")
        label.add_class("translation")
        label.append("(" + translate_locale(language) + ")")
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

                if current_direction is not None \
                and not (
                    self.user_collection
                    and not self.user_collection.allow_sorting
                ):
                    header.add_class("sorted")

                    if current_direction is PositiveExpression:
                        header.add_class("ascending")
                        sign = "-"
                    elif current_direction is NegativeExpression:
                        header.add_class("descending")

            order_param = sign + column.name

            if language:
                order_param += "." + language

            header.label["href"] = "?" + get_request_query(
                order = order_param,
                page = 0
            ).escape()

    def create_cell(self, item, column, language = None):
        cell = Element("td")

        if language:
            cell["dir"] = directionality.get(language)

        if (
            self.order
            and (column.name, language) in self._sorted_columns
            and not (
                self.user_collection
                and not self.user_collection.allow_sorting
            )
        ):
            cell.add_class("sorted")

        self._init_cell(cell, column, language)
        display = self.create_member_display(
            item,
            column,
            self.get_member_value(item, column)
        )
        cell.append(display)
        return cell

    def _init_cell(self, cell, column, language = None):
        cell.member = column
        cell.add_class(column.name + "_column")

        if language:
            cell.add_class(language)

