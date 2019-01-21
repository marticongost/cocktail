#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from datetime import date, datetime
from .translation import translations
from .helpers import (
    ca_possessive,
    ca_join,
    es_join,
    en_join,
    plural2
)

DATE_STYLE_NUMBERS = 1
DATE_STYLE_ABBR = 2
DATE_STYLE_TEXT = 3
DATE_STYLE_COMPACT_TEXT = 4

translations.load_bundle("cocktail.translations.datetimetranslations")

def month_name(month, language = None):
    if not isinstance(month, int):
        month = month.month
    return translations("cocktail.months.%d.name" % month, language)

def month_abbr(month, language = None):
    if not isinstance(month, int):
        month = month.month
    return translations("cocktail.months.%d.abbr" % month, language)

def weekday_name(day, language = None):
    if not isinstance(day, int):
        day = day.weekday()
    return translations("cocktail.weekdays.%d.name" % day, language)

def weekday_abbr(day, language = None):
    if not isinstance(day, int):
        day = day.weekday()
    return translations("cocktail.weekdays.%d.abbr" % day, language)

def _date_instance_ca(instance, style = DATE_STYLE_NUMBERS, relative = False):

    if relative:
        today = date.today()
        date_value = (
            instance.date() if isinstance(instance, datetime) else instance
        )
        day_diff = (date_value - today).days

        if day_diff == 0:
            return translations("cocktail.today")
        elif day_diff == -1:
            return translations("cocktail.yesterday")
        elif day_diff == 1:
            return translations("cocktail.tomorrow")
        elif 1 < day_diff <= 7:
            return weekday_name(instance) + u" que ve"
        elif -7 <= day_diff < 0:
            return weekday_name(instance) + u" passat"

    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("cocktail.date_format"))
    elif style == DATE_STYLE_ABBR:
        desc = u"%s %s" % (instance.day, month_abbr(instance))
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc
    elif style == DATE_STYLE_TEXT:
        desc = u"%s %s" % (
            instance.day,
            ca_possessive(month_name(instance).lower())
        )
        if not relative or today.year != instance.year:
            desc += u" de %d" % instance.year
        return desc
    elif style == DATE_STYLE_COMPACT_TEXT:
        desc = u"%s %s" % (
            instance.day,
            month_name(instance).lower(),
        )
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc

def _date_instance_es(instance, style = DATE_STYLE_NUMBERS, relative = False):

    if relative:
        today = date.today()
        date_value = (
            instance.date() if isinstance(instance, datetime) else instance
        )
        day_diff = (date_value - today).days

        if day_diff == 0:
            return translations("cocktail.today")
        elif day_diff == -1:
            return translations("cocktail.yesterday")
        elif day_diff == 1:
            return translations("cocktail.tomorrow")
        elif 1 < day_diff <= 7:
            return weekday_name(instance) + u" que viene"
        elif -7 <= day_diff < 0:
            return weekday_name(instance) + u" pasado"

    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("cocktail.date_format"))
    elif style == DATE_STYLE_ABBR:
        desc = u"%s %s" % (instance.day, month_abbr(instance))
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc
    elif style == DATE_STYLE_TEXT:
        desc = u"%s de %s" % (instance.day, month_name(instance).lower())
        if not relative or today.year != instance.year:
            desc += u" de %d" % instance.year
        return desc
    elif style == DATE_STYLE_COMPACT_TEXT:
        desc = u"%s %s" % (
            instance.day,
            month_name(instance).lower(),
        )
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc

def _date_instance_en(instance, style = DATE_STYLE_NUMBERS, relative = False):

    if relative:
        today = date.today()
        date_value = (
            instance.date() if isinstance(instance, datetime) else instance
        )
        day_diff = (date_value - today).days

        if day_diff == 0:
            return translations("cocktail.today")
        elif day_diff == -1:
            return translations("cocktail.yesterday")
        elif day_diff == 1:
            return translations("cocktail.tomorrow")
        elif 1 < day_diff <= 7:
            return u"Next " + weekday_name(instance).lower()
        elif -7 <= day_diff < 0:
            return u"Past " + weekday_name(instance).lower()

    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("cocktail.date_format"))
    elif style == DATE_STYLE_ABBR:
        desc = u"%s %s" % (month_abbr(instance.month), instance.day)
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc
    elif style == DATE_STYLE_TEXT:
        desc = u"%s %s" % (month_name(instance), instance.day)
        if not relative or today.year != instance.year:
            desc += u", %d" % instance.year
        return desc
    elif style == DATE_STYLE_COMPACT_TEXT:
        desc = u"%s %s" % (
            month_name(instance).lower(),
            instance.day,
        )
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc

def _date_instance_fr(instance, style = DATE_STYLE_NUMBERS, relative = False):

    if relative:
        today = date.today()
        date_value = (
            instance.date() if isinstance(instance, datetime) else instance
        )
        day_diff = (date_value - today).days

        if day_diff == 0:
            return translations("cocktail.today")
        elif day_diff == -1:
            return translations("cocktail.yesterday")
        elif day_diff == 1:
            return translations("cocktail.tomorrow")
        elif 1 < day_diff <= 7:
            return weekday_name(instance) + u" prochain"
        elif -7 <= day_diff < 0:
            return weekday_name(instance) + u" dernier"

    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("date format"))
    elif style == DATE_STYLE_ABBR:
        desc = u"%s %s" % (
            instance.day,
            month_abbr(instance)
        )
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc
    elif style in (DATE_STYLE_TEXT, DATE_STYLE_COMPACT_TEXT):
        desc = u"%s %s" % (instance.day, month_name(instance).lower())
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc

def _date_instance_pt(instance, style = DATE_STYLE_NUMBERS, relative = False):

    if relative:
        today = date.today()

    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("cocktail.date_format"))
    elif style == DATE_STYLE_ABBR:
        return u"%s %s %s" % (
            instance.day,
            month_abbr(instance),
            instance.year
        )
    elif style == DATE_STYLE_TEXT:
        return u"%s de %s de %s" % (
            instance.day,
            month_name(instance).lower(),
            instance.year
        )
    elif style == DATE_STYLE_COMPACT_TEXT:
        desc = u"%s %s" % (instance.day, month_name(instance).lower())
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc

def _date_instance_de(instance, style = DATE_STYLE_NUMBERS, relative = False):

    if relative:
        today = date.today()
        date_value = (
            instance.date() if isinstance(instance, datetime) else instance
        )
        day_diff = (date_value - today).days

        if day_diff == 0:
            return translations("cocktail.today")
        elif day_diff == -1:
            return translations("cocktail.yesterday")
        elif day_diff == 1:
            return translations("cocktail.tomorrow")
        elif 1 < day_diff <= 7:
            return u"Nächsten " + weekday_name(instance)
        elif -7 <= day_diff < 0:
            return u"Letzten " + weekday_name(instance)

    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("cocktail.date_format"))
    elif style == DATE_STYLE_ABBR:
        desc = u"%d.%s" % (instance.day, month_abbr(instance.month))
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc
    elif style in (DATE_STYLE_TEXT, DATE_STYLE_COMPACT_TEXT):
        desc = u"%d.%s" % (instance.day, month_name(instance))
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc

translations.define("datetime.date.instance",
    ca = _date_instance_ca,
    es = _date_instance_es,
    en = _date_instance_en,
    fr = _date_instance_fr,
    pt = _date_instance_pt,
    de = _date_instance_de
)

def _translate_time(value, include_seconds = True):
    return value.strftime("%H:%M" + (":%S" if include_seconds else ""))

translations.define("datetime.datetime.instance",
    ca = lambda instance,
        style = DATE_STYLE_NUMBERS,
        include_seconds = True,
        relative = False:
            _date_instance_ca(instance, style, relative)
            + (u" a les " if style == DATE_STYLE_TEXT else u" ")
            + _translate_time(instance, include_seconds),
    es = lambda instance,
        style = DATE_STYLE_NUMBERS,
        include_seconds = True,
        relative = False:
            _date_instance_es(instance, style, relative)
            + (u" a las " if style == DATE_STYLE_TEXT else u" ")
            + _translate_time(instance, include_seconds),
    en = lambda instance,
        style = DATE_STYLE_NUMBERS,
        include_seconds = True,
        relative = False:
            _date_instance_en(instance, style, relative)
            + (u" at " if style == DATE_STYLE_TEXT else u" ")
            + _translate_time(instance, include_seconds),
    fr = lambda instance,
        style = DATE_STYLE_NUMBERS,
        include_seconds = True,
        relative = False:
            _date_instance_fr(instance, style, relative)
            + (u" à " if style == DATE_STYLE_TEXT else u" ")
            + _translate_time(instance, include_seconds),
    pt = lambda instance, style = DATE_STYLE_NUMBERS, include_seconds = True:
        _date_instance_pt(instance, style)
        + u" " + _translate_time(instance, include_seconds),
    de = lambda instance,
        style = DATE_STYLE_NUMBERS,
        include_seconds = True,
        relative = False:
            _date_instance_de(instance, style, relative)
            + (u" um " if style == DATE_STYLE_TEXT else u" ")
            + _translate_time(instance, include_seconds)
            + (u" Uhr" if style == DATE_STYLE_TEXT else "")
)

translations.define("datetime.time.instance",
    lambda instance, include_seconds = True:
         _translate_time(instance, include_seconds)
)

def _create_time_span_function(span_format, forms, join):

    def time_span(span):

        # Without days
        if len(span) == 4:
            return span_format % span[:-1]

        # With days
        else:
            desc = []

            for value, form in zip(span, forms):
                if value:
                    desc.append("%d %s" % (value, plural2(value, *form)))

            return join(desc)

    return time_span

translations.define("cocktail.time_span",
    ca = _create_time_span_function(
        "%.2d.%.2d.%2d",
        [[u"dia", u"dies"],
         [u"hora", u"hores"],
         [u"minut", u"minuts"],
         [u"segon", u"segons"],
         [u"mil·lisegon", u"mil·lisegons"]],
        ca_join
    ),
    es = _create_time_span_function(
        "%.2d:%.2d:%2d",
        [[u"día", u"días"],
         [u"hora", u"horas"],
         [u"minuto", u"minutos"],
         [u"segundo", u"segundos"],
         [u"milisegundo", u"milisegundos"]],
        es_join
    ),
    en = _create_time_span_function(
        "%.2d:%.2d:%2d",
        [[u"day", u"days"],
         [u"hour", u"hours"],
         [u"minute", u"minutes"],
         [u"second", u"seconds"],
         [u"millisecond", u"milliseconds"]],
        en_join
    ),
    fr = _create_time_span_function(
        "%.2d:%.2d:%2d",
        [[u"jour", u"jours"],
         [u"heure", u"heures"],
         [u"minute", u"minutes"],
         [u"seconde", u"secondes"],
         [u"milliseconde", u"millisecondes"]],
        en_join
    )
)

def _date_range_ca(start, end):
    if start.year != end.year:
        return u"Del %s al %s" % (
            translations(start, style = DATE_STYLE_TEXT),
            translations(end, style = DATE_STYLE_TEXT)
        )
    elif start.month != end.month:
        return u"Del %d %s al %d %s de %d" % (
            start.day,
            ca_possessive(month_name(start)),
            end.day,
            ca_possessive(month_name(end)),
            start.year
        )
    else:
        return u"Del %d al %d %s de %d" % (
            start.day,
            end.day,
            ca_possessive(month_name(start)),
            start.year
        )

def _date_range_es(start, end):
    if start.year != end.year:
        return u"Del %s al %s" % (
            translations(start, style = DATE_STYLE_TEXT),
            translations(end, style = DATE_STYLE_TEXT)
        )
    elif start.month != end.month:
        return u"Del %d de %s al %d de %s de %d" % (
            start.day,
            month_name(start),
            end.day,
            month_name(end),
            start.year
        )
    else:
        return u"Del %d al %d de %s de %d" % (
            start.day,
            end.day,
            month_name(start),
            start.year
        )

def _date_range_en(start, end):
    if start.year != end.year:
        return u"From %s until %s" % (
            translations(start, style = DATE_STYLE_TEXT),
            translations(end, style = DATE_STYLE_TEXT)
        )
    elif start.month != end.month:
        return u"From the %s of %s until the %s of %s %d" % (
            translations("cocktail.ordinal", number = start.day),
            month_name(start),
            translations("cocktail.ordinal", number = end.day),
            month_name(end),
            start.year
        )
    else:
        return u"From the %s until the %s of %s %d" % (
            translations("cocktail.ordinal", number = start.day),
            translations("cocktail.ordinal", number = end.day),
            month_name(start),
            start.year
        )

def _date_range_fr(start, end):
    if start.year != end.year:
        return u"Du %s au %s" % (
            translations(start, style = DATE_STYLE_TEXT),
            translations(end, style = DATE_STYLE_TEXT)
        )
    elif start.month != end.month:
        return u"Du %s %s au %s %s %d" % (
            translations("cocktail.ordinal", number = start.day),
            month_name(start).lower(),
            translations("cocktail.ordinal", number = end.day),
            month_name(end).lower(),
            start.year
        )
    else:
        return u"Du %s au %s %s %d" % (
            translations("cocktail.ordinal", number = start.day),
            translations("cocktail.ordinal", number = end.day),
            month_name(start).lower(),
            start.year
        )

def _date_range_pt(start, end):
    if start.year != end.year:
        return u"De %s a %s" % (
            translations(start, style = DATE_STYLE_TEXT),
            translations(end, style = DATE_STYLE_TEXT)
        )
    elif start.month != end.month:
        return u"De %d de %s a %d de %s de %d" % (
            start.day,
            month_name(start).lower(),
            end.day,
            month_name(end).lower(),
            start.year
        )
    else:
        return u"De %d a %d de %s de %d" % (
            start.day,
            end.day,
            month_name(start).lower(),
            start.year
        )

translations.define("cocktail.date_range",
    ca = _date_range_ca,
    es = _date_range_es,
    en = _date_range_en,
    fr = _date_range_fr,
    pt = _date_range_pt
)

def translate_date_range(start, end):
    return translations("cocktail.date_range", start = start, end = end)

