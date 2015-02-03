#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from zope.interface import implements
from zope.index.text.interfaces import IPipelineElement
from zope.index.text.lexicon import Lexicon
from zope.index.text.okapiindex import OkapiIndex
from cocktail.events import when
from cocktail import schema
from cocktail.translations import iter_language_chain, descend_language_tree
from cocktail.translations import words
from cocktail.schema.expressions import normalize
from cocktail.persistence.datastore import datastore
from cocktail.persistence.persistentmapping import PersistentMapping
from cocktail.persistence.persistentobject import (
    PersistentObject,
    PersistentClass
)


class FullTextIndexProcessor(object):
    implements(IPipelineElement)
    stemming = True

    def __init__(self, locale, stemming):
        self.locale = locale
        self.stemming = stemming

    def process(self, sequence):
        if self.stemming:
            return words.get_stems(sequence, self.locale)
        else:
            terms = []
            processor = words.require_processor_for_locale(self.locale)
            for item in sequence:
                terms.extend(processor.split(processor.normalize(item)))
            return terms


schema.Member.full_text_indexed = False
PersistentObject.full_text_indexed = False
schema.Member.stemming = True

def _get_full_text_index_root(cls):
    root = cls

    for cls in cls.ascend_inheritance():
        if not cls.full_text_indexed:
            break
        root = cls

    return root

def _get_full_text_indexes(self):

    indexes = None
    key = self.full_text_index_key

    if key:
        indexes = datastore.root.get(key)

        if indexes is None:
            indexes = PersistentMapping()
            datastore.root[key] = indexes

    return indexes

PersistentClass._get_full_text_indexes = _get_full_text_indexes
schema.String._get_full_text_indexes = _get_full_text_indexes

def _get_full_text_index(self, language = None):

    if not self.full_text_indexed:
        return None

    indexes = self._get_full_text_indexes()

    if indexes is not None:
        index = indexes.get(language)
        if index is None:
            index = self.create_full_text_index(language)
            indexes[language] = index

    return index

PersistentClass.get_full_text_index = _get_full_text_index
schema.String.get_full_text_index = _get_full_text_index

def _set_full_text_index(self, language, index):

    indexes = self._get_full_text_indexes()

    if not indexes:
        raise ValueError(
            "No datastore key defined for the full text index of %s"
            % self
        )

    datastore.root[key] = index

PersistentClass.set_full_text_index = _set_full_text_index
schema.String.set_full_text_index = _set_full_text_index

PersistentClass._full_text_index_key = None
schema.String._full_text_index_key = None

def _get_full_text_index_key(self):

    key = self._full_text_index_key

    if not key and self.name:
        if self.schema:
            key = self.schema.full_name + "." + self.name
        else:
            key = _get_full_text_index_root(self).full_name

        key += "-full_text"

    return key

def _set_full_text_index_key(self, index_key):
    self._full_text_index_key = index_key


PersistentClass.full_text_index_key = property(
    _get_full_text_index_key,
    _set_full_text_index_key
)

schema.String.full_text_index_key = property(
    _get_full_text_index_key,
    _set_full_text_index_key
)

def _create_full_text_index(self, language):
    lexicon = Lexicon(
        FullTextIndexProcessor(language, self.stemming)
    )
    return OkapiIndex(lexicon)

PersistentClass.create_full_text_index = _create_full_text_index
schema.String.create_full_text_index = _create_full_text_index

def _persistent_class_index_text(self, obj, language = None):

    languages = None if language is None else (language,)

    extractor = obj.create_text_extractor(
        languages = languages,
        include_derived_languages = True
    )
    text_by_language = extractor.get_text_by_language()

    # Some of the requested languages may have no text; they should still be
    # removed from the index, so we select them explicitly.
    if languages is not None:
        for language in languages:
            if language not in text_by_language:
                for language in descend_language_tree(language):
                    text_by_language[language] = ""

    for language, text in text_by_language.iteritems():
        index = self.get_full_text_index(language)
        index.unindex_doc(obj.id)
        if text:
            index.index_doc(obj.id, text)

PersistentClass.index_text = _persistent_class_index_text

def _string_index_text(self, obj, language = None):

    if self.translated:
        if language is None:
            languages = obj.iter_translations(include_derived = True)
        else:
            languages = descend_language_tree(language, include_self = True)
    else:
        languages = (None,)

    for language in languages:
        index = self.get_full_text_index(language)
        index.unindex_doc(obj.id)
        text = obj.get(self, language)
        if text:
            text = normalize(text)
            index.index_doc(obj.id, text)

schema.String.index_text = _string_index_text

@when(PersistentObject.changed)
def _handle_changed(event):

    obj = event.source

    if obj.is_inserted and event.previous_value != event.value:

        # Reindex this specific member
        if obj._should_index_member_full_text(event.member):
            event.member.index_text(obj, event.language)

        # Only reindex whole objects when modifying a member included in the
        # object's text body (signaled by the 'text_search' attribute)
        if event.member.text_search:
            _cascade_index(obj, event.language, set())

def _cascade_index(obj, language, visited):

    if obj in visited:
        return

    visited.add(obj)

    # Reindex the whole object
    if obj.is_inserted and obj._should_index_member_full_text(obj.__class__):
        obj.__class__.index_text(obj, language)

    # Reindex related objects which include portions of the modified object in
    # their searchable text
    for member in obj.__class__.members().itervalues():
        related_end = getattr(member, "related_end", None)

        if related_end is not None and related_end.text_search:

            if isinstance(member, schema.Reference):
                related_object = obj.get(member)
                if related_object is not None:
                    _cascade_index(related_object, language, visited)

            elif isinstance(member, schema.Collection):
                related_items = obj.get(member)
                if related_items is not None:
                    for item in related_items:
                        _cascade_index(item, language, visited)

@when(PersistentObject.inserting)
def _handle_inserting(event):

    obj = event.source

    if obj._should_index_member_full_text(obj.__class__):
        obj.__class__.index_text(obj)

    for member in obj.__class__.iter_members():
        if obj._should_index_member_full_text(member):
            member.index_text(obj)

@when(PersistentObject.removing_translation)
def _handle_translation_removed(event):

    obj = event.source
    id = obj.id
    removed_language = event.language

    translated_members = []

    if obj._should_index_member_full_text(obj.__class__):
        translated_members.append(obj.__class__)

    translated_members.extend(
        member
        for member in obj.__class__.iter_members()
        if member.translated
        and obj._should_index_member_full_text(member)
    )

    for lang in obj.iter_derived_translations(
        removed_language,
        include_self = True
    ):
        for member in translated_members:
            index = member.get_full_text_index(lang)
            index.unindex_doc(id)

        if lang != removed_language:
            for chain_lang in iter_language_chain(lang):
                if (
                    chain_lang != removed_language
                    and chain_lang in obj.translations
                ):
                    for member in translated_members:

                        if isinstance(member, type):
                            text = obj.get_searchable_text(
                                languages = (chain_lang,)
                            )
                        else:
                            text = obj.get(member, chain_lang)
                            if text:
                                text = normalize(text)

                        if text:
                            index = member.get_full_text_index(lang)
                            index.index_doc(id, text)

                    break

@when(PersistentObject.deleting)
def _handle_deleting(event):

    obj = event.source
    id = obj.id
    members = [obj.__class__] + list(obj.__class__.iter_members())

    for member in members:
        if isinstance(member, (schema.String, PersistentClass)):
            indexes = member._get_full_text_indexes()
            if indexes is not None:
                for index in indexes.itervalues():
                    index.unindex_doc(id)

def _rebuild_full_text_index(self):

    datastore.root[self.full_text_index_key] = PersistentMapping()

    if isinstance(self, PersistentClass):
        persistent_type = _get_full_text_index_root(self)
    else:
        persistent_type = self.schema

    for obj in persistent_type.select():
        self.index_text(obj)

PersistentClass.rebuild_full_text_index = _rebuild_full_text_index
schema.String.rebuild_full_text_index = _rebuild_full_text_index

def _rebuild_full_text_indexes(cls, recursive = False, verbose = True):

    if cls.full_text_indexed and not any(
        isinstance(base, PersistentClass) and base.full_text_indexed
        for base in cls.bases
    ):
        if verbose:
            print "Rebuilding full text index for %s" % cls
        cls.rebuild_full_text_index()

    for member in cls.iter_members(recursive = False):
        if member.full_text_indexed:
            if verbose:
                print "Rebuilding full text index for %s" % member
            member.rebuild_full_text_index()

    if recursive:
        for derived in cls.derived_schemas():
            if derived.translation_source is None:
                derived.rebuild_full_text_indexes(True, verbose)

PersistentClass.rebuild_full_text_indexes = _rebuild_full_text_indexes

