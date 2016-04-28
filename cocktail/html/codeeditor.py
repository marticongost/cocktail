#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2009
"""
from cocktail.html.textarea import TextArea


class CodeEditor(TextArea):

    default_settings = {
        "indentUnit": 4
    }
    syntax_settings = {}
    editor_settings = {}
    syntax = None
    submodes = {
        "scss": ("css", "text/x-scss")
    }

    def __init__(self, *args, **kwargs):
        TextArea.__init__(self, *args, **kwargs)
        self.editor_settings = {}

    def _ready(self):

        TextArea._ready(self)

        self.add_resource("cocktail://codemirror/lib/codemirror.css")
        self.add_resource("cocktail://codemirror/lib/codemirror.js")
        self.add_resource("cocktail://scripts/CodeEditor.js")

        settings = self.default_settings.copy()
        submode_info = self.submodes.get(self.syntax)

        if submode_info:
            main_mode, submode = submode_info
        else:
            main_mode = self.syntax
            submode = self.syntax

        self.add_resource(
            "cocktail://codemirror/mode/%s/%s.js"
            % (main_mode, main_mode)
        )

        syntax_settings = self.syntax_settings.get(self.syntax)
        if syntax_settings:
            settings.update(syntax_settings)

        settings.update(self.editor_settings)
        settings.setdefault("mode", submode)
        self.set_client_param("codeMirrorSettings", settings)

