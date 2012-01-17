#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from time import time
from threading import Lock
from shutil import copyfileobj
from mimetypes import guess_type
import cherrypy
from simplejson import dumps
from cocktail.memoryutils import format_bytes
from cocktail.controllers.sessions import session
from cocktail.controllers.controller import Controller


class AsyncUploadController(Controller):

    uploader = None

    def __call__(self, *args, **kwargs):
        upload = self.uploader.process_request()
        return dumps({
            "id": upload.id,
            "filename": upload.filename,
            "type": upload.type,
            "size": format_bytes(upload.size)
        })


class AsyncUploader(object):

    session_prefix = "cocktail.async_upload."
    temp_folder = None
    upload_id = 0

    def __init__(self):
        self.lock = Lock()

    def process_request(self):
       
        # Create an upload and give it a unique identifier
        id = self._acquire_upload_id()
        upload = AsyncUpload(id)

        if cherrypy.request.headers.get("Content-Type") == "application/octet-stream":
            upload.filename = cherrypy.request.headers.get("X-File-Name")
            file = cherrypy.request.body
            if not file:
                raise ValueError("File upload failed: empty request body")
        else:
            try:
                upload_data = cherrypy.request.params["qqfile"]
            except KeyError:
                raise cherrypy.HTTPError(400)

            upload.filename = upload_data.filename
            file = upload_data.file

        # Get the file's size
        upload.size = int(cherrypy.request.headers.get("Content-Length", 0))

        # Determine the file's MIME type
        if upload.filename:
            type_guess = guess_type(upload.filename)
            upload.type = type_guess[0] if type_guess else None

        # Copy the uploaded file to a temporary location
        temp_path = self.get_temp_path(upload)
        with open(temp_path, "wb") as temp_file:
            copyfileobj(file, temp_file)

        # Save the metadata for the upload into the current session
        session[self.session_prefix + id] = upload

        return upload

    def get(self, upload_id):
        return session.get(self.session_prefix + upload_id)

    def get_temp_path(self, upload):
        return os.path.join(self.temp_folder, str("async-%s" % upload.id))

    def _acquire_upload_id(self):
        with self.lock:
            self.upload_id += 1
            return "%d-%d" % (time(), self.upload_id)


class AsyncUpload(object):
    
    __id = None
    file_name = None
    type = None
    size = 0

    def __init__(self, id, file_name = None, type = None, size = 0):
        self.__id = id
        self.file_name = file_name
        self.type = type
        self.size = size

    @property
    def id(self):
        return self.__id

    def __repr__(self):
        file_name = self.file_name
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join(
                repr(value)
                for value in (
                    self.__id,
                    self.file_name,
                    self.type,
                    format_bytes(self.size)
                )
                if value is not None
            )
        )

