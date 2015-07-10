#-*- coding: utf-8 -*-
u"""
Provides a class to describe members that handle sets of values.

@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         July 2008
"""
from cocktail.modeling import getter, InstrumentedDict, DictWrapper
from cocktail.schema.member import Member
from cocktail.schema.schemacollections import (
    Collection, RelationCollection, add, remove
)


class Mapping(Collection):
    """A collection that handles a set of key and value associations.

    @ivar keys: The schema that all keys in the collection must comply with.
        Specified as a member, which will be used as the validator for all
        values added to the collection.
    @type: L{Member<member.Member>}

    @ivar values: The schema that all values in the collection must comply
        with. Specified as a member, which will be used as the validator for
        all values added to the collection.
    @type: L{Member<member.Member>}
    """
    keys = None
    values = None
    default_type = dict
    get_item_key = None

    @getter
    def related_type(self):
        return self.values and self.values.type

    def translate_value(self, value, language = None, **kwargs):
        if self.keys and self.values and value:
            return u", ".join(
                u"%s: %s" % (
                    self.keys.translate_value(key),
                    self.values.translate_value(value)
                )
                for key, value in value.iteritems()
            )
        return Member.translate_value(self, value, language, **kwargs)

    # Validation
    #--------------------------------------------------------------------------
    def _items_validation(self, context):

        if self.name != "translations":

            # Item validation
            keys = self.keys
            values = self.values

            if keys is not None or values is not None:

                for key, value in context.value.iteritems():
                    if keys is not None:
                        for error in keys.get_errors(
                            key,
                            parent_context = context
                        ):
                            yield error
                    if values is not None:
                        for error in values.get_errors(
                            value,
                            collection_index = key,
                            parent_context = context
                        ):
                            yield error


# Generic add/remove methods
#------------------------------------------------------------------------------
def _mapping_add(collection, item):
    collection[item.id] = item

def _mapping_remove(collection, item):
    del collection[item.id]

add.implementations[dict] = _mapping_add
remove.implementations[dict] = _mapping_remove


# Relational data structures
#------------------------------------------------------------------------------

class RelationMapping(RelationCollection, InstrumentedDict):

    def __init__(self, items = None, owner = None, member = None):
        self.owner = owner
        self.member = member

        if items is not None and not isinstance(items, (dict, DictWrapper)):
            items = dict(
                (self.get_item_key(item), item)
                for item in items
            )

        InstrumentedDict.__init__(self, items)

    def get_item_key(self, item):
        if self.member.get_item_key:
            return self.member.get_item_key(self, item)
        else:
            raise TypeError("Don't know how to obtain a key from %s; "
                "the collection hasn't overriden its get_item_key() method."
                % item)

    def item_added(self, item):
        RelationCollection.item_added(self, item[1])

    def item_removed(self, item):
        RelationCollection.item_removed(self, item[1])

    def add(self, item):
        self[self.get_item_key(item)] = item

    def remove(self, item):
        del self[self.get_item_key(item)]

    def set_content(self, new_content):

        if new_content is None:
            added = []
            removed = self._items.items()
            self.clear()
        else:
            added = []
            removed = []
            previous_content = self._items

            if isinstance(new_content, (dict, DictWrapper)):
                new_content = new_content.iteritems()
            else:
                new_content = (
                    (self.get_item_key(item), item)
                    for item in new_content
                )

            self._items = dict(new_content)

            for key, old_value in previous_content.iteritems():
                if (
                    key not in self._items
                    or self._items.get(key) != old_value
                ):
                    removed.append((key, old_value))
                    self.item_removed((key, old_value))

            for key, new_value in self._items.iteritems():
                if (
                    key not in previous_content
                    or previous_content.get(key) != new_value
                ):
                    added.append((key, new_value))
                    self.item_added((key, new_value))

        if added or removed:
            self.changed(added = added, removed = removed)

