#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from simplejson import dumps
from cocktail.translations import get_language
from cocktail.html import Element, templates


class TinyMCE(Element):
    
    tag = None

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self.tinymce_params = {}
        self.add_resource(
            "/resources/scripts/tinymce/jscripts/tiny_mce/tiny_mce.js")

    def _build(self):
        self.textarea = templates.new("cocktail.html.TextArea")
        self.append(self.textarea)
        
    def _ready(self):

        Element._ready(self)

        if self.member:
            self.textarea._bind_name(self.member, self.language)

        if self.textarea["id"] is None:
            id = self.textarea["name"] + "_editor"
            if self.language:
                id += "-" + self.language
            self.textarea["id"] = id

        params = self.tinymce_params.copy()
        params.setdefault("language", get_language())
        params["mode"] = "exact"
        params["elements"] = self.textarea["id"]

        init_script = Element("script")
        init_script["type"] = "text/javascript"
        init_script.append("tinyMCE.init(%s)" % dumps(params))
        self.append(init_script)
    
    def _get_value(self):
        return self.textarea.value

    def _set_value(self, value):
        self.textarea.value = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the content of the rich text editor.
        @type: str
        """)

