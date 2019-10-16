#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
from .schemastrings import String
from cocktail.schema.exceptions import InvalidJSONError


class JSON(String):

    def _default_validation(self, context):
        """Validation rule for JSON values. Triggers an InvalidJSONError for
        values that can't be parsed as JSON.
        """
        try:
            json.loads(context.value)
        except ValueError:
            yield InvalidJSONError(context)

