#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.schema.accessors import get_accessor
from cocktail.schema.schemaobject import SchemaObject

def diff(
    source,
    target,
    schema = None,
    source_accessor = None,
    target_accessor = None,
    exclude = None,
    language_subset = None):
    """Obtains the set of members that differ between two items.

    @param source: The first item to compare.
    @param target: The other item to compare.

    @param schema: The schema used to compare both objects. Can be omitted if
        both objects are instances of the same
        L{SchemaObject<cocktail.schema.SchemaObject}.
    @type schema: L{Schema<cocktail.schema.Schema>}

    @param source_accessor: A data accessor used to extract data from the
        source item.
    @type source_accessor: L{Accessor<cocktail.accessors.Accessor>}
        subclass

    @param target_accessor: A data accessor used to extract data from the
        target item.
    @type target_accessor: L{Accessor<cocktail.accessors.Accessor>}
        subclass

    @param exclude: An optional filtering function that will be called to
        determine if a given member should be inspected or not.
    @type exclude: callable (L{member<cocktail.schema.member.Member>}) -> bool

    @param language_subset: Indicates the language that should be inspected in
        search of differences. Leave empty to consider all languages defined by
        either the source or the target objects.
    @type language_subset: str collection or None

    @return: An iterable sequence of member and language tuples.
    @rtype: (L{member<cocktail.schema.member.Member>}, str) iterable
    """
    if source_accessor is None:
        source_accessor = get_accessor(source)

    if target_accessor is None:
        target_accessor = get_accessor(target)

    if language_subset is not None and not isinstance(language_subset, set):
        language_subset = set(language_subset)

    # Try to infer the schema for SchemaObject instances
    if schema is None:
        if type(source) is type(target) \
        and isinstance(source, SchemaObject) \
        and isinstance(target, SchemaObject):
            schema = type(source)
        else:
            raise ValueError("The schema parameter for the diff() function "
                    "can't be ommitted if the two compared objects aren't "
                    "instances of the same SchemaObject derived class")

    for member in schema.members().itervalues():

        if exclude and exclude(member):
            continue

        key = member.name

        # Translated members
        if member.translated:

            source_languages = set(source_accessor.languages(source, key))
            target_languages = set(target_accessor.languages(target, key))
            languages = source_languages | target_languages
            if language_subset:
                languages &= language_subset

            for language in languages:

                source_value = source_accessor.get(
                    source,
                    key,
                    default = None,
                    language = language)

                target_value = target_accessor.get(
                    target,
                    key,
                    default = None,
                    language = language)

                if source_value != target_value:
                    yield (member, language)

        # Regular members
        else:
            source_value = source_accessor.get(source, key, default = None)
            target_value = target_accessor.get(target, key, default = None)
            if source_value != target_value:
                yield (member, None)

