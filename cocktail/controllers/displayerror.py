#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
import http.client
from traceback import extract_tb
from cgi import escape

import cherrypy


def format_error(error):
    lines = []
    for file, num, func, caller in reversed(extract_tb(error.__traceback__)):
        lines.append(
            """
            <li>
                <div>
                    <a href="sourcefile://%(file)s:%(num)d">%(file)s</a>,
                    line %(num)d,
                    in <span class="func">%(func)s</span>
                </div>
                <code>%(caller)s</code>
            </li>
            """ % {
                "file": _escape_error_property(file or "<?>"),
                "num": num,
                "func": _escape_error_property(func or "<?>"),
                "caller": _escape_error_property(caller or "<?>")
            }
        )

    return """
        <!DOCTYPE html>
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
                <title>%(error_type)s</title>
                <style type="text/css">
                    body {
                        font-family: Arial, sans-serif;
                        color: #333;
                        padding: 2em;
                    }
                    h1 {
                        font-size: 1.5em;
                        margin: 0;
                        margin-bottom: 1em;
                    }
                    ul {
                        list-style-type: none;
                        padding: 0;
                        margin: 0;
                        margin-bottom: 1.5em;
                    }
                    li {
                        padding: 0;
                        margin: 1em 0;
                    }
                    a {
                        color: #842020;
                        text-decoration: none;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                    .func {
                        font-weight: bold;
                    }
                    #error_desc {
                        background-color: #efe2e2;
                        padding: 0.8em;
                        margin-left: -0.8em;
                    }
                    #error_type {
                        color: #572828;
                        font-size: 1.1em;
                        font-weight: bold;
                    }
                    #error_message {
                        font-size: 1.1em;
                    }
                </style>
            </head>
            <body style="">
                <h1>%(status_code)s %(status_message)s</h1>
                <div id="error_desc">
                    <span id="error_type">%(error_type)s:</span>
                    <span id="error_message">%(error_message)s</span>
                </div>
                <ul>
                    %(traceback_lines)s
                </ul>
            </body>
        </html>
        """ % {
            "status_code": cherrypy.response.status,
            "status_message": (
                cherrypy.response.body
                or http.client.responses.get(cherrypy.response.status)
            ),
            "error_type": error.__class__.__name__,
            "error_message": escape(error.args[0]) if error.args else "",
            "traceback_lines": "\n".join(lines)
        }


def _escape_error_property(string):
    return escape(string)


def display_error():
    cherrypy.response.status = 500
    cherrypy.response.body = [format_error(sys.exc_info()[1])]

