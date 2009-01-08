#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from simplejson import dumps
from cocktail.schema import String
from cocktail.translations import get_language
from cocktail.html.element import Element
from cocktail.html.textbox import TextBox

class DatePicker(TextBox):

    def __init__(self, *args, **kwargs):
        TextBox.__init__(self, *args, **kwargs)
        
        self.add_resource(
            "/cocktail/scripts/jquery.js")
        self.add_resource(
            "/cocktail/scripts/jquery-ui.js")
        self.add_resource(
            "/cocktail/scripts/ui.datepicker-lang.js")
        self.add_resource(
            "/cocktail/styles/jquery-ui-themeroller.css")       
    
        self.date_picker_params = {}
    
    def _ready(self):
        
        TextBox._ready(self)
        id = self.require_id()
        
        params = self.date_picker_params.copy()
        
        for key, value in self.get_default_params().iteritems():
            params.setdefault(key, value)
       
        init_script = Element("script", type = "text/javascript")
        init_script.append(
            "jQuery(function () {\n"
            "\tjQuery('#%s')"
                ".datepicker($.extend({},$.datepicker.regional['%s'],%s));\n"
            "});"
            %  (id, get_language(), dumps(params))
        )
        self.add_head_element(init_script)
        
    def get_default_params(self):
        return {
            "ShowAnim": "slideDown",
            "changeFirstDay": False,
            "buttonImage": "/cocktail/images/calendar.png",
            "buttonImageOnly": True,
            "showOn": "both"
        }

    def _get_value(self):
        return self["value"]
    
    def _set_value(self, value):
        self["value"] = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the textbox's value.
        @type: str
        """)

