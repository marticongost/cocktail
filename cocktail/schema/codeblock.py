#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.stringutils import normalize_indentation
from cocktail.schema.schemastrings import String


class CodeBlock(String):

    language = None
    text_search = False

    def normalization(self, value):
        if value:
            if self.language == "python":
                value = value.replace("\r", "")
            value = normalize_indentation(value)
        return value

    def execute(self, obj, context):
        code = compile(
            obj.get(self), # code
            "<%r.%s>" % (obj, self.name), # label
            "exec"
        )
        exec(code, context)
        return context

