"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy

JSON_MIME_TYPE = "application/json"

def json_out(
    func = None,
    content_type = JSON_MIME_TYPE,
    encoding = "utf-8",
    **encode_options
):
    if func is None:
        def decorator(func):
            return _make_json_wrapper(
                func,
                content_type,
                encoding,
                **encode_options
            )

        return decorator

    return _make_json_wrapper(
        func,
        content_type,
        encoding,
        **encode_options
    )

def _make_json_wrapper(
    func,
    content_type,
    encoding,
    **encode_options
):
    def wrapper(*args, **kwargs):
        cherrypy.response.headers["Content-Type"] = "%s; %s" % (
            content_type,
            encoding
        )
        rvalue = func(*args, **kwargs)
        return json.dumps(rvalue, **encode_options).encode(encoding)

    return wrapper

def read_json(required_content_type = JSON_MIME_TYPE):
    if (
        required_content_type
        and cherrypy.request.headers["Content-Type"] != required_content_type
    ):
        raise cherrypy.HTTPError(
            400,
            "Expected a request of type " + required_content_type
        )

    length = int(cherrypy.request.headers["Content-Length"])
    json_string = cherrypy.request.body.read(length)
    return json.loads(json_string)

