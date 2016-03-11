#-*- coding: utf-8 -*-
u"""
Provides a method to export collections to different mime_types.

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			November 2009
"""
import os
import pyExcelerator
from decimal import Decimal
from collections import Counter
from cocktail.modeling import ListWrapper, SetWrapper, DictWrapper
from cocktail.translations import translations, get_language
from cocktail.typemapping import TypeMapping
from cocktail import schema

_exporters_by_mime_type = {}
_exporters_by_extension = {}

def register_exporter(func, mime_types, extensions = ()):
    """Declares a function used to write object collections to a file in a
    certain format.

    An exporter is bound to one or more MIME types, and optionally to one or
    more file extensions. If either MIME types or extensions are repeated
    between calls to this function, the newest registered exporter takes
    precedence.

    @param func: The writer function. It has a similar signature to the
        L{export_file} function, with the following differences:

            * It doesn't receive a mime_type parameter
            * X{dest} is normalized to an open file-like object
              (implementations shouldn't concern themselves with closing it)
            * X{members} is normalized to an ordered member sequence.
              Implementations should use this list when deciding which members
              to export; and if possible, its implied order should be
              preserved.
            * Implementations can add any number of keyword parameters in order
              to alter their output

    @type func: callable

    @param mime_types: The set of MIME types that the function is able to
        handle. If more than one MIME type is provided, they should all be
        aliases of one another: each exporter is expected to manage a single
        file type.
    @type mime_types: str sequence

    @param extensions: The set of file extensions that the function is able to
        handle.
    @type extensions: str sequence
    """
    for mime_type in mime_types:
        _exporters_by_mime_type[mime_type] = func
    for ext in extensions:
        _exporters_by_extension[ext] = func

def export_file(collection, dest, export_schema,
    mime_type = None,
    members = None,
    languages = None,
    **kwargs):
    """Writes a collection of objects to a file.

    @var collection: The collection of objects to write to the file.
    @type collection: iterable

    @var dest: The file to write the objects to. Can be an open file-like
        object, or a string pointing to a file system path.
    @type dest: str or file-like object

    @var export_schema: The schema describing the objects to write.
    @type export_schema: L{Member<cocktail.schema.Schema>}

    @var mime_type: The kind of file to write, indicated using its MIME type.
    @type mime_type: str

    @var members: Limits the members that will be written to the file to a
        subset of the given schema.
    @type members: L{Member<cocktail.schema.Member>} sequence

    @var languages: A collection of languages (ISO codes) to translate the
        translated members.
    @type languages: collection: iterable
    """
    exporter = None
    dest_is_string = isinstance(dest, basestring)

    if not mime_type and dest_is_string:
        title, ext = os.path.splitext(dest)
        if ext:
            try:
                exporter = _exporters_by_extension[ext]
            except KeyError:
                raise ValueError(
                    "There is no exporter associated with the %s extension"
                    % ext
                )

    if exporter is None and mime_type is None:
        raise ValueError("No MIME type specified")

    if exporter is None:
        try:
            exporter = _exporters_by_mime_type[mime_type]
        except KeyError:
            raise ValueError(
                "There is no exporter associated with the %s mime_type" % mime_type
            )

    if members is None and isinstance(export_schema, schema.Schema):
        members = export_schema.ordered_members()

    # Export the collection to the desired MIME type
    if dest_is_string:
        dest = open(dest, "w")
        try:
            exporter(
                collection,
                dest,
                export_schema,
                members,
                languages,
                **kwargs
            )
        finally:
            dest.close()
    else:
        exporter(
            collection,
            dest,
            export_schema,
            members,
            languages,
            **kwargs
        )

# Exporters
#------------------------------------------------------------------------------

class MSExcelExporter(object):

    def __init__(self):

        self.heading_style = pyExcelerator.XFStyle()
        self.heading_style.font = pyExcelerator.Font()
        self.heading_style.font.bold = True

        self.regular_style = pyExcelerator.XFStyle()
        self.regular_style.font = pyExcelerator.Font()

        def joiner(glue):
            return (
                lambda value:
                    glue.join(
                        unicode(self.export_value(item))
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
            (object, lambda value: unicode(value)),
            (str, lambda value: value.encode("utf-8")),
            (unicode, None),
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
            (schema.Member, description_or_raw_value),
        ))

        self.member_exporters = {}
        self.member_column_types = {}

    def get_member_is_translated(self, member):
        return member.translated

    def get_columns(self, collection, export_schema, members, languages):
        columns = []
        for member in members:
            columns.extend(self.get_member_columns(member, languages))
        return columns

    def get_member_columns(self, member, languages):

        column_type = (
            self.member_column_types.get(member)
            or MSExcelMemberColumn
        )

        if self.get_member_is_translated(member):
            for language in languages:
                yield column_type(self, member, language)
        else:
            yield column_type(self, member)

    def get_member_heading(self, member, language):
        if language:
            return u"%s (%s)" % (
                translations(member),
                translations("locale", locale = language)
            )
        else:
            return translations(member)

    def export_member_value(self, obj, member, value, language = None):
        exporter = self.member_exporters.get(member.name)

        if exporter is None:
            exporter = self.member_type_exporters.get(member.__class__)

        if exporter is not None:
            value = exporter(obj, member, value, language)

        return value

    def export_value(self, value):
        exporter = self.type_exporters.get(value.__class__)

        if exporter is None:
            return value
        else:
            return exporter(value)

    def create_workbook(
        self,
        collection,
        export_schema,
        members,
        languages = None
    ):
        workbook = pyExcelerator.Workbook()
        sheet = workbook.add_sheet('0')

        if languages is None:
            languages = [get_language()]

        if isinstance(export_schema, schema.Schema):

            # Determine columns
            columns = self.get_columns(
                collection,
                export_schema,
                members,
                languages
            )

            # Column headings
            for j, column in enumerate(columns):
                sheet.write(
                    0,
                    j,
                    column.heading,
                    column.heading_style or self.heading_style
                )

            # Cells
            for i, obj in enumerate(collection):
                for j, column in enumerate(columns):
                    cell_value = self.export_value(column.get_cell_value(obj))
                    cell_style = (
                        column.get_cell_style(obj)
                        or self.regular_style
                    )
                    sheet.write(i + 1, j, cell_value, cell_style)
        else:
            # Column headings
            sheet.write(0, 0, schema.name or "", self.heading_style)

            for row, obj in enumerate(collection):
                cell_content = self.export_value(obj)
                sheet.write(row + 1, 0, cell_content)

        return workbook


class MSExcelColumn(object):

    def __init__(self,
        exporter,
        language = None,
        heading = "",
        heading_style = None,
        style = None
    ):
        self.exporter = exporter
        self.language = language
        self.heading = heading
        self.heading_style = heading_style
        self.style = style

    def get_cell_value(self, obj):
        return ""

    def get_cell_style(self, obj):
        return self.style or self.exporter.regular_style


class MSExcelMemberColumn(MSExcelColumn):

    def __init__(self,
        exporter,
        member,
        language = None,
        heading = None,
        heading_style = None,
        style = None
    ):
        MSExcelColumn.__init__(
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

    def get_cell_value(self, obj):
        return self.exporter.export_member_value(
            obj,
            self.member,
            obj.get(self.member.name, self.language),
            self.language
        )


def description_or_raw_value(obj, member, value, language = None):
    if member.__class__.translate_value is not schema.Member.translate_value:
        desc = member.translate_value(value, language = language)
        return desc or value
    else:
        return value

default_msexcel_exporter = MSExcelExporter()


def export_msexcel(
    collection,
    dest,
    export_schema,
    members,
    languages = None,
    msexcel_exporter = default_msexcel_exporter
):
    """Method to export a collection to MS Excel."""
    workbook = msexcel_exporter.create_workbook(
        collection,
        export_schema,
        members,
        languages
    )
    workbook.save(dest)

register_exporter(
    export_msexcel,
    ["application/msexcel", "application/vnd.ms-excel"],
    [".xls"]
)

