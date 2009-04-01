#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.html import Element
from cocktail.html.databoundcontrol import DataBoundControl


class FileUploadBox(Element, DataBoundControl):

    tag = "input"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataBoundControl.__init__(self)
        self["type"] = "file"

    def _ready(self):

        if self.member:

            # Limit accepted mime types
            if self.member["mime_type"].enumeration:
                self["accept"] = \
                    ",".join(ct for ct in self.member["mime_type"].enumeration)
    
        Element._ready(self)

    def insert_into_form(self, form, field_instance):
        # Overriden to automatically change the encoding of the enclosing form
        # to multipart/form-data
        if not form.embeded:
            form["enctype"] = "multipart/form-data"
        field_instance.append(self)

