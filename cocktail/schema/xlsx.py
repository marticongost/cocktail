"""Export object sets to a MS Excel file.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any, Iterable, Mapping, Sequence
import os
from copy import deepcopy
from decimal import Decimal
from collections import Counter

from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font

from cocktail.modeling import ListWrapper, SetWrapper, DictWrapper
from cocktail.translations import translations, get_language, translate_locale
from cocktail.typemapping import TypeMapping
from .member import Member
from .schema import Schema
from .schemaobject import SchemaObject

MIME_TYPE = (
    "application/"
    "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


class Exporter:

    heading_style = {
        "font": Font(bold=True)
    }

    regular_style = {}

    def __init__(self):

        self.heading_style = deepcopy(self.heading_style)
        self.regular_style = deepcopy(self.regular_style)

        def joiner(glue):
            return (
                lambda value:
                    glue.join(
                        str(self.export_value(item))
                        for item in value
                    )
            )

        multiline = joiner(u"\n")

        def multiline_mapping(value):
            return u"\n".join(
                u"%s: %s" % (k, v)
                for k, v in value.iteritems()
            )

        def multiline_count(value):
            return u"\n".join(
                u"%s: %s" % (k, v)
                for k, v in value.most_common()
            )

        self.type_exporters = TypeMapping((
            (object, lambda value: str(value)),
            (str, None),
            (type(None), lambda value: ""),
            (bool, None),
            (int, None),
            (float, None),
            (Decimal, None),
            (tuple, joiner(u", ")),
            (list, multiline),
            (set, multiline),
            (ListWrapper, multiline),
            (SetWrapper, multiline),
            (Counter, multiline_count),
            (dict, multiline_mapping),
            (DictWrapper, multiline_mapping)
        ))

        self.member_type_exporters = TypeMapping((
            (Member, description_or_raw_value),
        ))

        self.member_exporters = {}
        self.member_column_types = {}

    def get_member_is_translated(self, member: Member) -> bool:
        return member.translated

    def get_columns(
            self,
            members: Sequence[Member],
            languages: Sequence[str]) -> Sequence["Column"]:

        columns = []

        for member in members:
            columns.extend(self.get_member_columns(member, languages))

        return columns

    def get_member_columns(
            self,
            member: Member,
            languages: Sequence[str]) -> Sequence["Column"]:

        column_type = (
            self.member_column_types.get(member)
            or MemberColumn
        )

        if self.get_member_is_translated(member):
            for language in languages:
                yield column_type(self, member, language)
        else:
            yield column_type(self, member)

    def get_member_heading(self, member: Member, language: str) -> str:
        if language:
            return u"%s (%s)" % (
                translations(member),
                translate_locale(language)
            )
        else:
            return translations(member)

    def export_member_value(
            self,
            obj: SchemaObject,
            member: Member,
            value: Any,
            language: str = None) -> Any:

        exporter = self.member_exporters.get(member.name)

        if exporter is None:
            exporter = self.member_type_exporters.get(member.__class__)

        if exporter is not None:
            value = exporter(obj, member, value, language)

        return value

    def export_value(self, value: Any) -> str:

        exporter = self.type_exporters.get(value.__class__)

        if exporter is None:
            return value
        else:
            return exporter(value)

    def create_workbook(
        self,
        objects: Iterable[SchemaObject],
        members: Sequence[Member] = None,
        languages: Sequence[str] = None
    ):
        workbook = Workbook(write_only=True)
        sheet = workbook.create_sheet()

        if languages is None:
            languages = [get_language()]

        # Determine columns
        columns = self.get_columns(members, languages)

        # Column headings
        header = []

        for column in columns:
            cell = WriteOnlyCell(sheet, value=column.heading)
            self.apply_style(
                cell,
                column.heading_style or self.heading_style
            )
            header.append(cell)

        sheet.append(header)

        # Cells
        for obj in objects:
            row = []
            for column in columns:
                cell_value = self.export_value(column.get_cell_value(obj))
                cell = WriteOnlyCell(sheet, value=cell_value)
                self.apply_style(
                    cell,
                    column.get_cell_style(obj) or self.regular_style
                )
                row.append(cell)
            sheet.append(row)

        return workbook

    def apply_style(self, cell: WriteOnlyCell, style: Mapping):
        for key, value in style.items():
            setattr(cell, key, value)


class Column(object):

    def __init__(
        self,
        exporter: Exporter,
        language: str = None,
        heading: str = None,
        heading_style: dict = None,
        style: dict = None
    ):
        self.exporter = exporter
        self.language = language
        self.heading = heading
        self.heading_style = heading_style
        self.style = style

    def get_cell_value(self, obj: SchemaObject) -> Any:
        return ""

    def get_cell_style(self, obj: SchemaObject) -> Mapping:
        return self.style or self.exporter.regular_style


class MemberColumn(Column):

    def __init__(
        self,
        exporter: Exporter,
        member: Member,
        language: str = None,
        heading: str = None,
        heading_style: dict = None,
        style: dict = None
    ):
        Column.__init__(
            self,
            exporter,
            language = language,
            heading =
                exporter.get_member_heading(member, language)
                if heading is None
                else heading,
            heading_style = heading_style,
            style = style
        )
        self.member = member

    def get_cell_value(self, obj: SchemaObject) -> Any:
        return self.exporter.export_member_value(
            obj,
            self.member,
            obj.get(self.member.name, self.language),
            self.language
        )


def description_or_raw_value(
        obj: SchemaObject,
        member: Member,
        value: str,
        language: str = None) -> str:

    if member.__class__.translate_value is not Member.translate_value:
        desc = member.translate_value(value, language = language)
        return desc or value
    else:
        return value


default_exporter = Exporter()

