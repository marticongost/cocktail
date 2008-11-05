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
        
        if self.member:
            self._bind_name(self.member, self.language)
        
            if self["id"] is None:
                id = self["name"]
                self["id"] = id
            
            params = self.date_picker_params.copy()
            params.setdefault("ShowAnim", "slideDown")
            params.setdefault("changeFirstDay", False)
            params.setdefault("buttonImage", "/cocktail/images/calendar.gif")
            params.setdefault("buttonImageOnly", True)
            params.setdefault("showOn", "both")
            
            init_script = Element("script")
            init_script["type"] = "text/javascript"            
            init_script.append("jQuery('#%s').datepicker($.extend({},$.datepicker.regional['%s'],%s));" % \
                (self["id"],get_language(),dumps(params)))
            self.append(init_script)
        
        TextBox._ready(self)    

    def _get_value(self):
        return self["value"]
    
    def _set_value(self, value):
        self["value"] = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the textbox's value.
        @type: str
        """)

