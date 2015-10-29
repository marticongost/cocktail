#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.translations.translation import translations
from cocktail.html.textbox import TextBox
from cocktail.schema.schemadates import Date, DateTime, Time


class DatePicker(TextBox):

    def __init__(self, *args, **kwargs):
        TextBox.__init__(self, *args, **kwargs)
        self.add_resource("/cocktail/scripts/jquery-ui.js")
        self.add_resource("/cocktail/scripts/ui.datepicker-lang.js")
        self.add_resource("/cocktail/scripts/jquery.maskedinput.js")
        self.add_resource("/cocktail/scripts/DatePicker.js")
        self.date_picker_params = {}

    def _ready(self):

        TextBox._ready(self)

        if isinstance(self.member, (DateTime, Time)):
            self.set_client_param("hasTime", True)

        if isinstance(self.member, (DateTime, Date)):
            self.set_client_param("hasDate", True)

            params = self.date_picker_params.copy()

            for key, value in self.get_default_params().iteritems():
                params.setdefault(key, value)

            self.set_client_param("datePickerParams", params)

    def get_jformat(self):
        return translations("jquery_date format")

    def get_default_params(self):
        return {
            "ShowAnim": "slideDown",
            "dateFormat": self.get_jformat(),
            "changeFirstDay": False,
            "buttonImage": "/cocktail/images/calendar.png",
            "buttonImageOnly": True,
            "defaultValue": self["value"],
            "showOn": "both",
            "prevText": "&lt;",
            "nextText": "&gt;"
        }

