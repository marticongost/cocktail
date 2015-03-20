#-*- coding: utf-8 -*-
u"""Helper functions for translating strings into multiple languages.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import ListWrapper
from cocktail.translations.translation import get_language

CA_APOSTROPHE_LETTERS = u"haàeèéiíoòóuú"

def ca_apostrophe(word):
    norm_word = word.lstrip('"')
    return norm_word and norm_word[0].lower() in CA_APOSTROPHE_LETTERS

def ca_possessive(text):
    if ca_apostrophe(text):
        return u"d'" + text
    else:
        return u"de " + text

def ca_possessive_with_article(text):
    if ca_apostrophe(text):
        return u"de l'" + text
    else:
        return u"del " + text

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

    join.func_name = language + "_join"
    return join

ca_join = create_join_function("ca", u", ", u" i ")
ca_either = create_join_function("ca", u", ", u" o ")
es_join = create_join_function("es", u", ", u" y ")
es_either = create_join_function("ca", u", ", u" o ")
en_join = create_join_function("en", u", ", u" and ")
en_either = create_join_function("ca", u", ", u" or ")
de_join = create_join_function("de", u", ", u" und ")
de_either = create_join_function("ca", u", ", u" oder ")
fr_join = create_join_function("fr", u", ", u" et ")
fr_either = create_join_function("fr", u", ", u" ou ")

def join(sequence):
    join_func = globals()[get_language() + "_join"]
    return join_func(sequence)

def either(sequence):
    either_func = globals()[get_language() + "_join"]
    return either_func(sequence)

def plural2(count, singular, plural):
    if count == 1:
        return singular
    else:
        return plural

