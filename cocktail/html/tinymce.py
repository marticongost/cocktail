#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from warnings import warn
from simplejson import dumps
from cocktail.translations import get_language
from cocktail.html import Element, templates
from cocktail.html.databoundcontrol import data_bound


class TinyMCE(Element):
    
    class __metaclass__(Element.__metaclass__):
        def __init__(cls, name, bases, members):
            Element.__metaclass__.__init__(cls, name, bases, members)
            if "tinymce_params" not in members:
                cls.tinymce_params = {}

    default_tinymce_params = {} # deprecated
    tinymce_params = {}

    def __init__(self, *args, **kwargs):
        self.tinymce_params = {}
        Element.__init__(self, *args, **kwargs)
        data_bound(self)
        self.add_resource(
            "/cocktail/scripts/TinyMCE.js")
        self.add_resource(
            "/resources/scripts/tinymce/jscripts/tiny_mce/tiny_mce_src.js")

    def aggregate_tinymce_params(self):

        params = {}

        for cls in reversed(self.__class__.__mro__):
            class_params = getattr(cls, "tinymce_params", None)
            if class_params:
                params.update(class_params)

        if self.default_tinymce_params:
            warn(
                "TinyMCE.default_tinymce_params is deprecated, use "
                "TinyMCE.tinymce_params instead",
                DeprecationWarning,
                stacklevel = 2
            )
            params.update(self.default_tinymce_params)

        params.update(self.tinymce_params)
        return params

    def _build(self):
        self.textarea = templates.new("cocktail.html.TextArea")
        self.append(self.textarea)
        self.binding_delegate = self.textarea
        
    def _ready(self):
        Element._ready(self)
        params = self.aggregate_tinymce_params()

        # Override essential TinyMCE parameters
        params["mode"] = "exact"
        params["language"] = get_language()
        params["elements"] = self.textarea.require_id()

        self.set_client_param("tinymceSettings", params);
    
    def _get_value(self):
        return self.textarea.value

    def _set_value(self, value):
        self.textarea.value = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the content of the rich text editor.
        @type: str
        """)

