#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
import cherrypy
import hashlib
from mimetypes import guess_type
from cocktail.translations import translations
from cocktail.memoryutils import parse_bytes, format_bytes
from cocktail import schema
from cocktail.schema.exceptions import ValidationError

translations.load_bundle("cocktail.controllers.fileupload")


class FileUpload(schema.Schema):

    _special_copy_keys = (
        schema.Schema._special_copy_keys | set(["async_uploader"])
    )

    chunk_size = 8192
    normalization = None
    hash_algorithm = None
    __max_size = None

    async = False
    async_uploader = None
    async_upload_url = None
    async_prefix = "async-"

    meaningless_mime_types = (
        "application/octet-stream",
        "application/force-download"
    )

    mime_type_corrections = {
        "image/pjpeg": "image/jpeg",
        "image/x-png": "image/png"
    }

    def __init__(self, *args, **kwargs):

        schema.Schema.__init__(self, *args, **kwargs)

        file_name_kw = {}
        file_size_kw = {"min": 0}
        mime_type_kw = {}

        file_name_properties = kwargs.get("file_name_properties")
        if file_name_properties:
            file_name_kw.update(file_name_properties)

        file_size_properties = kwargs.get("file_size_properties")
        if file_size_properties:
            file_size_kw.update(file_size_properties)

        file_size_kw.setdefault(
            "translate_value",
            lambda value, language = None, **kwargs:
                format_bytes(value)
                if value or value == 0 else ""
        )

        mime_type_properties = kwargs.get("mime_type_properties")
        if mime_type_properties:
            mime_type_kw.update(mime_type_properties)

        self.add_member(schema.String("file_name", **file_name_kw))
        self.add_member(schema.Integer("file_size", **file_size_kw))
        self.add_member(schema.String("mime_type", **mime_type_kw))

    def __deepcopy__(self, memo):
        copy = schema.Schema.__deepcopy__(self, memo)
        copy.async_uploader = self.async_uploader
        return copy

    def _get_max_size(self):
        return self.__max_size

    def _set_max_size(self, max_size):

        if isinstance(max_size, str):
            max_size = parse_bytes(max_size)

        self.__max_size = max_size

    max_size = property(
        _get_max_size,
        _set_max_size,
        doc = """Gets or sets the maximum size allowed for this upload.

        Can be set to an integer (indicating a number of bytes) or to a string
        using a format accepted by L{cocktail.memory_utils.parse_bytes}.
        """
    )

    def parse_request_value(self, reader, value):

        # Handle asynchronous uploads
        async_upload = None
        file = None

        if isinstance(value, str):

            if self.async \
            and self.async_uploader is not None \
            and value.startswith(self.async_prefix):
                try:
                    async_file_id = value[len(self.async_prefix):]
                except:
                    pass
                else:
                    async_upload = self.async_uploader.get(async_file_id)

            if async_upload is None:
                value = None
            else:
                value = async_upload

        if value is None or not value.filename:
            return None

        file_name = value.filename

        if isinstance(file_name, str):
            file_name = file_name.decode("utf-8")

        # IE insists in sending the full local path of uploaded files, which is
        # completely absurd. Strip path information from the file name.
        file_name = file_name.split("\\")[-1]

        upload = {
            "id": async_upload.id if async_upload else None,
            "file_name": file_name,
            "mime_type": value.type,
            "file_size": None,
            "file_hash": None
        }

        # Support per-extension MIME types
        if value.type in self.meaningless_mime_types:
            mime_type_guess = guess_type(file_name, strict = False)
            if mime_type_guess:
                upload["mime_type"] = mime_type_guess[0]

        # Map bad MIME types to their proper values
        good_mime_type = self.mime_type_corrections.get(upload["mime_type"])
        if good_mime_type:
            upload["mime_type"] = good_mime_type

        dest = self.get_file_destination(upload)
        dest_file = None
        chunk_size = self.chunk_size

        hash = None \
            if self.hash_algorithm is None \
            else hashlib.new(self.hash_algorithm)
        size = 0

        # Read a first chunk of the uploaded file
        if async_upload:
            temp_path = self.async_uploader.get_temp_path(async_upload.id)
            file = open(temp_path, "rb")
        else:
            file = value.file

        chunk = file.read(chunk_size)

        # Don't write to the destination if no file has been uploaded
        if chunk and dest:
            dest_file = open(dest, "wb")

        # Read the complete file, in chunks
        try:
            while chunk:
                if dest:
                    dest_file.write(chunk)

                if hash is not None:
                    hash.update(chunk)

                size += len(chunk)
                chunk = file.read(chunk_size)
        finally:
            if dest_file:
                dest_file.close()

        if not dest:
            file.seek(0)
            upload["file"] = file

        if not size:
            upload = None
        else:
            upload["file_size"] = size

            if hash is not None:
                upload["file_hash"] = hash.hexdigest()

        return upload

    def get_file_destination(self, upload):
        return None

    def _create_default_instance(self):
        return None

    def _default_validation(self, context):

        for error in schema.Schema._default_validation(self, context):
            yield error

        file_size = context.get_value("file_size")

        if file_size:
            max_size = self.resolve_constraint(self.max_size, context)
            if max_size and file_size > max_size:
                yield FileSizeTooBigError(context, max_size)


class FileSizeTooBigError(ValidationError):

    def __init__(self, context, max_size):
        ValidationError.__init__(self, context)
        self.max_size = max_size

    def __str__(self):
        return "%s (shouldn't exceed %s)" % format_bytes(self.max_size)

