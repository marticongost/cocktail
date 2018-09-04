#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""

class ComponentFileError(Exception):

    def __init__(self, full_name, referrer = None, reference_type = None):
        Exception.__init__(self)
        self.full_name = full_name
        self.referrer = referrer
        self.reference_type = reference_type

    def __str__(self):
        desc = "Can't find component " + self.full_name

        if self.referrer or self.reference_type:

            if self.reference_type == "base":
                ref_desc = "extended"
            elif self.reference_type == "dependency":
                ref_desc = "added as an explicit dependency"
            elif self.reference_type == "part":
                ref_desc = "instantiated"
            else:
                ref_desc = "referenced"

            desc += " (%s by %s)" % (
                ref_desc,
                self.referrer.full_name if self.referrer else "?"
            )

        return desc


class ParseError(Exception):

    def __init__(self, component_loader, message, line_number = None):
        self.message = message
        self.component_loader = component_loader
        self.line_number = line_number

    def __str__(self):

        desc = "%s (at component %s" % (
            self.message,
            self.component_loader.component.full_name
        )

        source_file = self.component_loader.component.source_file
        if source_file:
            desc += ", file %s" % source_file

        if self.line_number:
            desc += ", line %d)" % self.line_number
        else:
            desc += ")"

        return desc

