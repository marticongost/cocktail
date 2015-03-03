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


class TinyMCE(Element):

    class __metaclass__(Element.__metaclass__):
        def __init__(cls, name, bases, members):
            Element.__metaclass__.__init__(cls, name, bases, members)
            if "tinymce_params" not in members:
                cls.tinymce_params = {}

    tinymce_params = {}

    def __init__(self, *args, **kwargs):
        self.tinymce_params = {}
        Element.__init__(self, *args, **kwargs)

    def aggregate_tinymce_params(self):

        params = {}

        for cls in reversed(self.__class__.__mro__):
            class_params = getattr(cls, "tinymce_params", None)
            if class_params:
                params.update(class_params)

        params.update(self.tinymce_params)
        return params

    def _build(self):
        self.add_resource("/cocktail/scripts/tinymce/js/tinymce/tinymce.min.js")
        self.add_client_code("tinymce.init(this.tinymceSettings);")
        self.textarea = templates.new("cocktail.html.TextArea")
        self.data_binding_delegate = self.textarea
        self.append(self.textarea)
        self.data_binding_delegate = self.textarea

    def _ready(self):
        Element._ready(self)
        params = self.aggregate_tinymce_params()

        # Override essential TinyMCE parameters
        params["mode"] = "exact"
        params["language"] = get_language()
        params["elements"] = self.textarea.require_id()

        self.set_client_param("tinymceSettings", params);

