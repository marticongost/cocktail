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

    default_settings = {}
    syntax_settings = {}
    editor_settings = {}
    syntax = None

    def __init__(self, *args, **kwargs):
        TextArea.__init__(self, *args, **kwargs)
        self.editor_settings = {}

    def _ready(self):

        TextArea._ready(self)

        self.add_resource("cocktail://codemirror/lib/codemirror.css")
        self.add_resource("cocktail://codemirror/lib/codemirror.js")
        self.add_resource("cocktail://codemirror/mode/%s/%s.js" % (
            self.syntax,
            self.syntax
        ))

        settings = self.default_settings.copy()

        syntax_settings = self.syntax_settings.get(self.syntax)
        if syntax_settings:
            settings.update(syntax_settings)

        settings.update(self.editor_settings)
        settings["mode"] = self.syntax

        self.add_client_code(
            "CodeMirror.fromTextArea(this, %s)"
            % dumps(settings)
        )

