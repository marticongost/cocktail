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
from cocktail.translations import translations

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
            exporter(collection, dest, schema, members, **kwargs)
        finally:
            dest.close()
    else:
        exporter(collection, dest, schema, members, **kwargs)

# Exporters
#------------------------------------------------------------------------------

def export_msexcel(collection, dest, schema, members):
    """Method to export a collection to MS Excel."""

    book = pyExcelerator.Workbook()
    sheet = book.add_sheet('0')

    # Header style
    header_style = pyExcelerator.XFStyle()
    header_style.font = pyExcelerator.Font()
    header_style.font.bold = True
    
    # Sheet content
    def get_cell_content(member, value):                
        if value is None:
            return ""
        elif isinstance(value, (list, set, ListWrapper, SetWrapper)):
            return "\n".join(get_cell_content(member, item)
                            for item in value)
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, Decimal):
            return float(value)
        else:
            return member.translate_value(value)

    if isinstance(schema, Schema):
        # Column headers
        for col, member in enumerate(members):
            label = translations(member)
            sheet.write(0, col, label, header_style)

        for row, item in enumerate(collection):
            for col, member in enumerate(members):

                if member.name == "element":
                    value = translations(item)
                elif member.name == "class":
                    value = translations(item.__class__.name)
                else:
                    value = item.get(member.name)

                cell_content = get_cell_content(member, value)
                sheet.write(row + 1, col, cell_content)
    else:
        # Column headers
        sheet.write(0, 0, schema.name or "", header_style)

        for row, item in enumerate(collection):
            cell_content = get_cell_content(schema, item)
            sheet.write(row + 1, 0, cell_content)

    book.save(dest)

register_exporter(
    export_msexcel, 
    ["application/msexcel", "application/vnd.ms-excel"], 
    [".xls"]
)

