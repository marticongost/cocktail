#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2009
"""
from simplejson import dumps
from cocktail.html import Element
from cocktail.html.textarea import TextArea


class CodeEditor(TextArea):

    resources_uri = "/cocktail/codemirror/"

    base_settings = {
        "path": resources_uri + "js/",
        "indentUnit": 4,
        "width": "",
        "height": ""        
    }

    editor_settings = {}

    syntax_settings = {
        "javascript": {
            "parserfile": [
                "tokenizejavascript.js",
                "parsejavascript.js"
            ],
            "stylesheet": resources_uri + "css/jscolors.css",
            "autoMatchParens": True
        },
        "html": {
            "parserfile": [
                "parsexml.js",
                "parsecss.js",
                "tokenizejavascript.js",
                "parsejavascript.js",
                "parsehtmlmixed.js"
            ],
            "stylesheet": [
                resources_uri + "css/xmlcolors.css",
                resources_uri + "css/jscolors.css",
                resources_uri + "css/csscolors.css"
            ]
        },
        "xml": {
            "parserfile": "parsexml.js",
            "stylesheet": resources_uri + "css/xmlcolors.css",
            "useHTMLKludges": False
        },
        "css": {
            "parserfile": "parsecss.js",
            "stylesheet": resources_uri + "css/csscolors.css"
        },
        "sparql": {
            "parserfile": "parsesparql.js",
            "stylesheet": resources_uri + "css/sparqlcolors.css"
        },
        "php": {
            "parserfile": [
                "parsexml.js",
                "parsecss.js",
                "tokenizejavascript.js",
                "parsejavascript.js",
                "../contrib/php/js/tokenizephp.js",
                "../contrib/php/js/parsephp.js",
                "../contrib/php/js/parsephphtmlmixed.js"
            ],
            "stylesheet": [
                resources_uri + "css/xmlcolors.css",
                resources_uri + "css/jscolors.css",
                resources_uri + "css/csscolors.css",
                resources_uri + "css/phpcolors.css"
            ]
        },
        "python": {
            "parserfile": "../contrib/python/js/parsepython.js",
            "stylesheet": resources_uri + "css/pythoncolors.css",
            "parserConfig": {"pythonVersion": 2, "strictErrors": True}
        },
        "sql": {
            "parserfile": "../contrib/sql/js/parsesql.js",
            "stylesheet": resources_uri + "css/sqlcolors.css"
        },
        "lua": {
            "parserfile": "../contrib/lua/js/parselua.js",
            "stylesheet": resources_uri + "css/luacolors.css"
        },
        "ruby": {
            "parserfile": "../contrib/ruby/js/parseruby.js",
            "stylesheet": resources_uri + "css/rubycolors.css"
        }
    }

    def __init__(self, *args, **kwargs):
        TextArea.__init__(self, *args, **kwargs)
        self.editor_settings = {}

    def _ready(self):
        
        self.add_resource(self.resources_uri + "js/codemirror.js")

        settings = self.base_settings.copy()
        
        if self._syntax:
            settings.update(self.syntax_settings.get(self._syntax))

        settings.update(self.editor_settings)
        
        self.add_client_code("CodeMirror.fromTextArea('%s', %s)" % (
            self.require_id(),
            dumps(settings)
        ))

    _syntax = None

    def _get_syntax(self):
        return self._syntax

    def _set_syntax(self, syntax):

        if syntax not in self.syntax_settings:            
            raise ValueError("Unknown syntax: %s" % syntax)
        
        self._syntax = syntax

    syntax = property(_get_syntax, _set_syntax)

