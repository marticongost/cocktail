#-*- coding: utf-8 -*-
u"""Helper functions for translating strings into multiple languages.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import ListWrapper

CA_APOSTROPHE_LETTERS = u"haàeèéiíoòóuú"

def ca_apostrophe(word):
    return word and word[0].lower() in CA_APOSTROPHE_LETTERS

def ca_possessive(text):
    if ca_apostrophe(text):
        return u"d'" + text
    else:
        return u"de " + text

def create_join_function(language, sep1, sep2):

    def join(sequence):
        if not isinstance(sequence, (list, ListWrapper)):
            sequence = list(sequence)

        if len(sequence) > 1:
            return sep1.join(sequence[:-1]) + sep2 + sequence[-1]
        else:
            return sequence[0]

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

def plural2(count, singular, plural):
    if count == 1:
        return singular
    elif count > 1:
        return plural

