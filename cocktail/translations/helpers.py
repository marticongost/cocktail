#-*- coding: utf-8 -*-
"""Helper functions for translating strings into multiple languages.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from decimal import Decimal
from cocktail.modeling import ListWrapper
from cocktail.translations.translation import get_language, iter_language_chain

CA_APOSTROPHE_LETTERS = "haàeèéiíoòóuú1"

def ca_apostrophe(word):
    norm_word = word.lstrip('"')
    return norm_word and norm_word[0].lower() in CA_APOSTROPHE_LETTERS

def ca_apostrophe_choose(no_apostrophe_particle, apostrophe_particle, word):
    if ca_apostrophe(word):
        return "%s'%s" % (apostrophe_particle, word)
    else:
        return "%s %s" % (no_apostrophe_particle, word)

def ca_possessive(text):
    if ca_apostrophe(text):
        return "d'" + text
    else:
        return "de " + text

def ca_possessive_with_article(text):
    if ca_apostrophe(text):
        return "de l'" + text
    else:
        return "del " + text

def create_join_function(language, sep1, sep2):

    def join(sequence):
        if not isinstance(sequence, (list, ListWrapper)):
            sequence = list(sequence)

        count = len(sequence)

        if count > 1:
            return sep1.join(sequence[:-1]) + sep2 + sequence[-1]
        elif count == 1:
            return sequence[0]
        else:
            return ""

    join.__name__ = language + "_join"
    return join

ca_join = create_join_function("ca", ", ", " i ")
ca_either = create_join_function("ca", ", ", " o ")
es_join = create_join_function("es", ", ", " y ")
es_either = create_join_function("ca", ", ", " o ")
en_join = create_join_function("en", ", ", " and ")
en_either = create_join_function("ca", ", ", " or ")
de_join = create_join_function("de", ", ", " und ")
de_either = create_join_function("ca", ", ", " oder ")
fr_join = create_join_function("fr", ", ", " et ")
fr_either = create_join_function("fr", ", ", " ou ")

def join(sequence):
    g = globals()
    for lang in iter_language_chain():
        join_func = g.get(lang + "_join")
        if join_func:
            return join_func(sequence)

    raise ValueError("No join function for language " + get_language())

def either(sequence):
    g = globals()
    for lang in iter_language_chain():
        join_func = g.get(lang + "_either")
        if join_func:
            return join_func(sequence)

    raise ValueError("No either function for language " + get_language())

def plural2(count, singular, plural):

    if not isinstance(count, (int, float, Decimal)):
        count = len(count)

    if count == 1:
        return singular
    else:
        try:
            return plural % count
        except TypeError:
            return plural

