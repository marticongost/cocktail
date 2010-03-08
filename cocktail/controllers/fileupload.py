#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
import cherrypy
import hashlib
from cocktail import schema

class FileUpload(schema.Schema):
    
    chunk_size = 8192
    normalization = None
    hash_algorithm = None

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

        mime_type_properties = kwargs.get("mime_type_properties")
        if mime_type_properties:
            mime_type_kw.update(mime_type_properties)

        self.add_member(schema.String("file_name", **file_name_kw))
        self.add_member(schema.Integer("file_size", **file_size_kw))
        self.add_member(schema.String("mime_type", **mime_type_kw))

    def parse_request_value(self, reader, value):       
        
        file_name = unicode(value.filename, 'utf-8')

        # IE insists in sending the full local path of uploaded files, which is
        # completely absurd. Strip path information from the file name.
        file_name = file_name.split("\\")[-1]

        upload = {
            "file_name": file_name,
            "mime_type": value.type,
            "file_size": None,
            "file_hash": None
        }
        
        dest = self.get_file_destination(upload)
        dest_file = None
        chunk_size = self.chunk_size
        
        hash = None \
            if self.hash_algorithm is None \
            else hashlib.new(self.hash_algorithm)
        size = 0

        # Read a first chunk of the uploaded file
        chunk = value.file.read(chunk_size)
        
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
                chunk = value.file.read(chunk_size)
        finally:
            if dest_file:
                dest_file.close()

        if not dest:
            value.file.seek(0)
            upload["file"] = value.file

        if not size:
            upload = None
        else:
            upload["file_size"] = size

            if hash is not None:
                upload["file_hash"] = hash.digest()

        return upload

    def get_file_destination(self, upload):
        return None

