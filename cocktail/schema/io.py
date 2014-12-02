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
from cocktail.schema import Schema
from cocktail.modeling import ListWrapper, SetWrapper
from cocktail.translations import translations, get_language
from cocktail.typemapping import TypeMapping

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

def export_file(collection, dest, schema,
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

    @var schema: The schema describing the objects to write.
    @type schema: L{Member<cocktail.schema.Schema>}

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

    if members is None and isinstance(schema, Schema):
        members = schema.ordered_members()

    # Export the collection to the desired MIME type
    if dest_is_string:
        dest = open(dest, "w")
        try:
            exporter(collection, dest, schema, members, languages, **kwargs)
        finally:
            dest.close()
    else:
        exporter(collection, dest, schema, members, languages, **kwargs)

# Exporters
#------------------------------------------------------------------------------
msexcel_exporters = TypeMapping()
msexcel_exporters[type(None)] = lambda member, value: ""
msexcel_exporters[object] = lambda member, value: member.translate_value(value)
msexcel_exporters[bool] = lambda member, value: member.translate_value(value)
msexcel_exporters[int] = lambda member, value: value
msexcel_exporters[int] = lambda member, value: value
msexcel_exporters[float] = lambda member, value: value
msexcel_exporters[Decimal] = lambda member, value: float(value)

def _iterables_to_msexcel(member, value):
    return "\n".join(msexcel_exporters[type(item)](member.items, item) 
                    for item in value)

msexcel_exporters[list] = _iterables_to_msexcel
msexcel_exporters[set] = _iterables_to_msexcel
msexcel_exporters[ListWrapper] = _iterables_to_msexcel
msexcel_exporters[SetWrapper] = _iterables_to_msexcel

def export_msexcel(collection, dest, schema, members, languages = None):
    """Method to export a collection to MS Excel."""

    book = pyExcelerator.Workbook()
    sheet = book.add_sheet('0')

    if languages is None:
        languages = [get_language()]

    # Header style
    header_style = pyExcelerator.XFStyle()
    header_style.font = pyExcelerator.Font()
    header_style.font.bold = True
    
    if isinstance(schema, Schema):
        # Column headers
        col = 0
        for member in members:
            if member.translated:
                for language in languages:
                    label = "%s (%s)" % (
                        translations(member), translations(language)
                    )
                    sheet.write(0, col, label, header_style)
                    col += 1
            else:
                label = translations(member)
                sheet.write(0, col, label, header_style)
                col += 1

        for row, item in enumerate(collection):
            col = 0
            for member in members:

                if member.translated:
                    for language in languages:
                        value = item.get(member.name, language)
                        cell_content = msexcel_exporters[type(value)](member, value)
                        sheet.write(row + 1, col, cell_content)
                        col += 1
                else:
                    if member.name == "element":
                        value = translations(item)
                    elif member.name == "class":
                        value = translations(item.__class__.name)
                    else:
                        value = item.get(member.name)

                    cell_content = msexcel_exporters[type(value)](member, value)
                    sheet.write(row + 1, col, cell_content)
                    col += 1
    else:
        # Column headers
        sheet.write(0, 0, schema.name or "", header_style)

        for row, item in enumerate(collection):
            cell_content = msexcel_exporters[type(item)](schema, item)
            sheet.write(row + 1, 0, cell_content)

    book.save(dest)

register_exporter(
    export_msexcel, 
    ["application/msexcel", "application/vnd.ms-excel"], 
    [".xls"]
)

