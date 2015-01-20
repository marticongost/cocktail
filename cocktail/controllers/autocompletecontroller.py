#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from simplejson import dumps
import cherrypy
from cocktail import schema
from cocktail.schema.expressions import Self
from cocktail.persistence import PersistentClass, Query
from cocktail.controllers import Controller


class AutocompleteController(Controller):

    member = None

    def __init__(self, member, *args, **kwargs):
        Controller.__init__(self, *args, **kwargs)
        if isinstance(member, PersistentClass):
            member = schema.Reference(type = member)
        self.member = member

    def __call__(self, query):
        self.query = query
        cherrypy.response.headers["Content-Type"] = "application/json"
        return Controller.__call__(self)

    def render(self):

        yield u"["

        record = {}
        glue = u""

        for item in self.get_items():
            yield glue
            glue = u","
            record["value"] = self.get_entry_value(item)
            record["label"] = self.get_entry_label(item)
            yield dumps(record)

        yield u"]"

    def get_items(self):
        items = self.member.get_possible_values()

        if not isinstance(items, Query):
            items = self.member.type.select()
            items.base_collection = items

        if self.query:
            self.apply_search(items)

        return items

    def apply_search(self, items):
        items.add_filter(
            Self.search(self.query, match_mode = "prefix")
        )

    def get_entry_value(self, item):
        return self.member.serialize_request_value(item)

    def get_entry_label(self, item):
        return self.member.translate_value(item)

