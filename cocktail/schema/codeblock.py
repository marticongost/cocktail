#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema.schemastrings import String


class CodeBlock(String):

    language = None
    text_search = False

    def normalization(self, value):
        if value:
            value = value.strip()
            if self.language == "python":
                value = value.replace("\r", "")
        return value

    def execute(self, obj, context):
        code = compile(
            obj.get(self), # code
            "<%r.%s>" % (obj, self.name), # label
            "exec"
        )
        exec code in context
        return context

