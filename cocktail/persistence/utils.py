#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from .datastore import datastore

def undo_last_transaction():
    db = datastore.db
    db.undo(db.undoInfo()[0]["id"])
    datastore.commit()

def solidify_defaults(cls):
    for instance in cls.select():
        for member in cls.members().itervalues():
            if member.expression is not None:
                continue
            if member.translated:
                for language in instance.translations:
                    instance.get(member, language)
            else:
                instance.get(member)

def is_broken(obj):
    return hasattr(obj, "__Broken_Persistent__")

def is_broken_instance_of(obj, cls_name):
    bp = getattr(obj, "__Broken_Persistent__", None)
    return bp is not None and bp.__name__ == cls_name

def remove_broken_type(
    full_name,
    existing_bases = (),
    relations = (),
    excluded_relations = (),
    languages = None
):
    relations = set(relations)

    if existing_bases:
        indexes = [existing_bases[0].index]
        full_text_indexes = []

        if languages:
            langauges = [None] + list(languages)

        for base in existing_bases:
            indexes.append(base.keys)

            if languages and base.full_text_indexed:
                for language in languages:
                    full_text_indexes.append(
                        base.get_full_text_index(language)
                    )

            for member in base.members(recursive = False).itervalues():
                if member.indexed:
                    indexes.append(member.index)

                if languages and member.full_text_indexed:
                    for language in languages:
                        full_text_indexes.append(
                            member.get_full_text_index(language)
                        )

                if (
                    isinstance(member, schema.RelationMember)
                    and member.bidirectional
                ):
                    relations.add(member.related_end)

        keys = datastore.root.pop(full_name + "-keys", None)
        if keys:
            for id in keys:
                for index in indexes:
                    try:
                        index.remove(id)
                    except KeyError:
                        pass

                for index in full_text_indexes:
                    index.unindex_doc(id)

    if excluded_relations:
        relations.difference_update(excluded_relations)

    if relations:
        local_name = full_name[full_name.rfind(".") + 1:]

        for relation in relations:
            priv_key = "_" + relation.name

            if isinstance(relation, schema.Reference):
                for instance in relation.schema.select():
                    try:
                        value = getattr(instance, priv_key)
                        if is_broken_instance_of(value, local_name):
                            delattr(instance, priv_key)
                    except AttributeError:
                        pass

            elif isinstance(relation, schema.Collection):
                for instance in relation.schema.select():
                    items = getattr(instance, priv_key, None)
                    if items is not None:
                        if isinstance(items, (
                            schema.RelationList,
                            schema.RelationSet,
                            schema.RelationOrderedSet
                        )):
                            items = items._items

                        for item in list(items):
                            if is_broken_instance_of(item, local_name):
                                schema.remove(items, item)

    for key in list(datastore.root):
        if key.startswith(full_name + ".") or key.startswith(full_name + "-"):
            del datastore.root[key]

