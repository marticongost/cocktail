#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
import cherrypy
from traceback import extract_tb
from cgi import escape

def format_error(error_type, error, traceback):

    lines = []
    for file, num, func, caller in extract_tb(traceback):
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
                    html {
                        background-color: #442F2F;
                    }
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #ebdada;
                        color: #333;
                        padding: 2em;
                        padding-top: 1.5em;
                        margin: 1em;
                        border: 1px solid #a05757;
                        border-radius: 0.6em;
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
                        display: inline-block;
                        border: 2px solid #a05757;
                        border-radius: 0.3em;
                        background-color: #ddc7c7;
                        padding: 0.6em;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
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
                <h1>500 Internal Server Error</h1>
                <ul>
                    %(traceback_lines)s
                </ul>
                <div id="error_desc">
                    <span id="error_type">%(error_type)s:</span>
                    <span id="error_message">%(error_message)s</span>
                </div>
            </body>
        </html>
        """ % {
            "error_type": error_type.__name__,
            "error_message": escape(error.message),
            "traceback_lines": "\n".join(lines)
        }

def _escape_error_property(string):
    if isinstance(string, unicode):
        string = string.encode("utf-8")
    return escape(string)

def display_error():
    cherrypy.response.status = 500
    cherrypy.response.body = [format_error(*sys.exc_info())]

