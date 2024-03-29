#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
import mimetypes
import cherrypy
import rfc6266
from cherrypy.lib import cptools, httputil, file_generator_limited
from cocktail.events import Event, when
from cocktail.html.resources import resource_repositories, SASSCompilation


class FilePublication(object):

    use_xsendfile = False

    def __init__(self):
        self.processors = []

    def produce_file(
        self,
        file,
        content_type = None,
        processing_options = None
    ):
        if isinstance(file, str):
            path = file
            try:
                file = open(path, "rb")
            except (OSError, IOError):
                file = None
        else:
            path = getattr(file, "name", None)

        file_info = {
            "file": file,
            "path": path,
            "content_type": content_type
        }

        if processing_options:
            file_info.update(processing_options)

        for processor in self.processors:
            processor(file_info)

        return file_info

    def serve_file(
        self,
        file,
        content_type = None,
        disposition = None,
        name = None,
        processing_options = None
    ):
        file_info = self.produce_file(file, content_type, processing_options)
        file = file_info["file"]

        if file is None:
            raise cherrypy.NotFound()

        return self.serve_raw_file(
            file,
            content_type = file_info["content_type"],
            disposition = disposition,
            name = name
        )

    def serve_raw_file(
        self,
        file,
        content_type = None,
        disposition = None,
        name = None
    ):
        # Adapted from CherryPy's serve_file(), modified to work with file-like
        # objects

        response = cherrypy.response
        st = None

        if isinstance(file, str):

            path = file

            if not os.path.isabs(path):
                raise ValueError("'%s' is not an absolute path." % path)

            try:
                st = os.stat(path)
            except OSError:
                raise cherrypy.NotFound()

            if stat.S_ISDIR(st.st_mode):
                raise cherrypy.NotFound()

            response.headers['Last-Modified'] = httputil.HTTPDate(st.st_mtime)
            cptools.validate_since()
            file = open(path, "rb")
        else:
            path = getattr(file, "name", None)
            if path:
                try:
                    st = os.stat(path)
                except OSError:
                    pass
            else:
                if not hasattr(file, "read"):
                    raise ValueError(
                        "Expected a file-like object, got %r instead "
                        "(object has no read() method)"
                        % file
                    )
                if not hasattr(file, "seek"):
                    raise ValueError(
                        "Can't serve file-like object %r "
                        "(object has no seek() method)"
                        % file
                    )
                if not hasattr(file, "tell"):
                    raise ValueError(
                        "Can't serve file-like object %r "
                        "(object has no tell() method)"
                        % file
                    )

        # Set the content type
        if content_type is None:

            if path:
                content_type = mimetypes.guess_type(path)[0]

            if not content_type:
                content_type = "text/plain"

        response.headers["Content-Type"] = content_type

        # Set the content disposition
        if disposition is not None:
            cd = disposition
            if not name and path:
                name = os.path.basename(path)
            if name:
                cd = rfc6266.build_header(name, cd)
            response.headers["Content-Disposition"] = cd

        if self.use_xsendfile and path:
            response.headers["X-Sendfile"] = path
            return ""

        # Find the size of the file
        if st is None:
            start = file.tell()
            file.seek(0, 2) # Move to the end of the file
            c_len = file.tell() - start
            file.seek(start)
        else:
            c_len = st.st_size

        # HTTP/1.0 didn't have Range/Accept-Ranges headers, or the 206 code
        if cherrypy.request.protocol >= (1, 1):
            response.headers["Accept-Ranges"] = "bytes"
            r = httputil.get_ranges(
                cherrypy.request.headers.get('Range'),
                c_len
            )
            if r == []:
                response.headers['Content-Range'] = "bytes */%s" % c_len
                message = "Invalid Range (first-byte-pos greater than Content-Length)"
                raise cherrypy.HTTPError(416, message)
            if r:
                if len(r) == 1:
                    # Return a single-part response.
                    start, stop = r[0]
                    if stop > c_len:
                        stop = c_len
                    r_len = stop - start
                    response.status = "206 Partial Content"
                    response.headers['Content-Range'] = ("bytes %s-%s/%s" %
                                                           (start, stop - 1, c_len))
                    response.headers['Content-Length'] = r_len
                    file.seek(start)
                    response.body = file_generator_limited(file, r_len)
                else:
                    # Return a multipart/byteranges response.
                    response.status = "206 Partial Content"
                    import mimetools
                    boundary = mimetools.choose_boundary()
                    ct = "multipart/byteranges; boundary=%s" % boundary
                    response.headers['Content-Type'] = ct
                    if "Content-Length" in response.headers:
                        # Delete Content-Length header so finalize() recalcs it.
                        del response.headers["Content-Length"]

                    def file_ranges():
                        # Apache compatibility:
                        yield "\r\n"

                        for start, stop in r:
                            yield "--" + boundary
                            yield "\r\nContent-type: %s" % content_type
                            yield ("\r\nContent-range: bytes %s-%s/%s\r\n\r\n"
                                   % (start, stop - 1, c_len))
                            file.seek(start)
                            for chunk in file_generator_limited(file, stop-start):
                                yield chunk
                            yield "\r\n"
                        # Final boundary
                        yield "--" + boundary + "--"

                        # Apache compatibility:
                        yield "\r\n"
                    response.body = file_ranges()
            else:
                response.headers['Content-Length'] = c_len
                response.body = file
        else:
            response.headers['Content-Length'] = c_len
            response.body = file

        return response.body

    def file_publisher(self, path):
        """Creates a CherryPy handler that serves the specified file."""

        @cherrypy.expose
        def file_publisher_handler(
            controller,
            content_type = None,
            disposition = None,
            name = None
        ):
            return self.serve_file(path, content_type, disposition, name)

        return file_publisher_handler

    def folder_publisher(self, path):

        root = os.path.normpath(path)

        @cherrypy.expose
        def folder_publisher_handler(controller, *args, **kwargs):

            requested_path = path
            for arg in args:
                requested_path = os.path.join(requested_path, arg)

            # Prevent serving files outside the specified root path
            if not os.path.normpath(requested_path).startswith(root):
                raise cherrypy.HTTPError(403)

            return self.serve_file(
                requested_path,
                disposition = kwargs.get("disposition")
            )

        return folder_publisher_handler


file_publication = FilePublication()


class SASSPreprocessor(object):

    sass_compiler_options = {}
    ignore_cached_files = False

    def __call__(self, file_info):

        path = file_info["path"]

        if not path:
            return

        base_path, ext = os.path.splitext(path)
        if ext not in (".css", ".map"):
            return

        inner_path, inner_ext = os.path.splitext(base_path)
        if inner_ext != ".scss":
            return

        base_name, theme = os.path.splitext(inner_path)
        scss_path = base_name + ".scss"

        if not theme:
            theme = "default"
        else:
            theme = theme.lstrip(".")

        try:
            scss_st = os.stat(scss_path)
        except OSError:
            pass
        else:
            css_path = base_path + ".css"
            map_path = base_path + ".map"

            try:
                css_st = os.stat(css_path)
            except OSError:
                css_st = None

            try:
                map_st = os.stat(map_path)
            except OSError:
                map_st = None

            if (
                self.ignore_cached_files
                or (css_st is None or scss_st.st_mtime > css_st.st_mtime)
                or (map_st is None or scss_st.st_mtime > map_st.st_mtime)
            ):
                sass = SASSCompilation(theme = theme)
                css, source_map = sass.compile(
                    filename = scss_path,
                    source_map_filename = map_path,
                    **self.get_sass_compiler_options()
                )

                if isinstance(css, str):
                    css = css.encode("utf-8")

                if isinstance(source_map, str):
                    source_map = source_map.encode("utf-8")

                open(css_path, "wb").write(css)
                open(map_path, "wb").write(source_map)

            file_info["file"] = open(path)

    def get_sass_compiler_options(self):
        return self.sass_compiler_options.copy()


try:
    import sass
except ImportError:
    sass = None
else:
    file_publication.processors.append(SASSPreprocessor())

