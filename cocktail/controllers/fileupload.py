#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail import schema


class FileUpload(schema.Schema):
    
    chunk_size = 8192
    normalization = None

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
        
        upload = {            
            "file_name": value.filename,
            "mime_type": value.type
        }
        
        dest = self.get_file_destination(upload)
        chunk_size = self.chunk_size
        
        # Measure size & write
        if dest:
            size = 0

            # Read a first chunk of the uploaded file
            chunk = value.file.read(chunk_size)
            
            # Don't write to the destination if no file has been uploaded
            if chunk:
                dest_file = open(dest, "wb")

                # Write the first chunk and the rest of the file to the
                # destination
                try:
                    while chunk:
                        dest_file.write(chunk)
                        size += len(chunk)
                        chunk = value.file.read(chunk_size)
                finally:
                    dest_file.close()
        
        # Measure size
        else:
            size = 0
            while True:
                chunk = value.file.read(chunk_size)
                if not chunk:
                    break
                size += len(chunk)
        
            value.file.seek(0)
            upload["file"] = value.file

        if not size:
            upload = None
        else:
            upload["file_size"] = size

        return upload

    def get_file_destination(self, upload):
        return None

