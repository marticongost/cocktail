#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
import datetime
from simplejson import dumps
from cocktail.schema import String
from cocktail.translations import get_language
from cocktail.translations.translation import translations, translate
from cocktail.html import templates
from cocktail.html.element import Element
from cocktail.html.textbox import TextBox
from cocktail.html.databoundcontrol import DataBoundControl
from cocktail.schema.schemadates import Date, DateTime, Time

class DatePicker(TextBox):         

    def __init__(self, *args, **kwargs):
        TextBox.__init__(self, *args, **kwargs)
        DataBoundControl.__init__(self)
        self.add_resource(
            "/cocktail/scripts/jquery.js")
        self.add_resource(
            "/cocktail/scripts/jquery-ui.js")
        self.add_resource(
            "/cocktail/scripts/ui.datepicker-lang.js")
        self.add_resource(
            "/cocktail/styles/jquery-ui-themeroller.css")
        self.add_resource(
                "/resources/scripts/timepicker.js")       
    
        self.date_picker_params = {}             
    
    def _ready(self):
                
        id = self.require_id()
        
        if isinstance(self.member, (DateTime, Time)):
            self.add_resource(
                "/cocktail/scripts/jquery.maskedinput.js")
                
            if isinstance(self.member, Time):
                self.add_class("time")
        
        if isinstance(self.member, (DateTime, Date)):
        
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
            
            if isinstance(self.member, DateTime):
                self.add_class("timepickr")                       
            
            
        
        TextBox._ready(self)
       
    def get_jformat(self):
        return translate("jquery_date format", get_language())    
        
    def get_default_params(self):
        return {
            "ShowAnim": "slideDown",
            "dateFormat": self.get_jformat(),
            "changeFirstDay": False,
            "buttonImage": "/cocktail/images/calendar.png",
            "buttonImageOnly": True,
            "defaultValue": self._get_value(),    
            "showOn": "both"
        }

    def _get_value(self):
        return self["value"]
    
    def _set_value(self, value):
        HOUR_FORMAT = "%H:%M:%S"
        if value: 
            if isinstance(value, datetime.date):
                self["value"] = value.strftime(translate("date format", get_language()))
            elif isinstance(value, datetime.datetime):
                self["value"] = value.strftime(translate("date format", get_language()) + " " + HOUR_FORMAT)
            elif isinstance(value, datetime.time):
                self["value"] = value.strftime(HOUR_FORMAT) 
        else:   
            self["value"] = value            

    value = property(_get_value, _set_value, doc = """
        Gets or sets the textbox's value.
        @type: str
        """)

