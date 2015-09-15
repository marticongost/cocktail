#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import re
from datetime import datetime, date, timedelta
from decimal import Decimal
from cocktail.pkgutils import get_full_name
from cocktail.stringutils import decapitalize
from cocktail.translations.translation import translations
from cocktail.translations.helpers import (
    ca_possessive,
    ca_possessive_with_article,
    ca_join,
    ca_either,
    es_join,
    es_either,
    en_join,
    en_either,
    plural2
)
from cocktail.schema.expressions import (
    Constant,
    PositiveExpression
)

translations.define("PersistentObject",
    ca = u"Objecte",
    es = u"Objeto",
    en = u"Object"
)

translations.define("bool-instance",
    ca = lambda instance: u"Sí" if instance else u"No",
    es = lambda instance: u"Sí" if instance else u"No",
    en = lambda instance: u"Yes" if instance else u"No"
)

translations.define("Any",
    ca = u"Qualsevol",
    es = u"Cualquiera",
    en = u"Any"
)

translations.define("Accept",
    ca = u"Acceptar",
    es = u"Aceptar",
    en = u"Accept"
)

translations.define("Cancel",
    ca = u"Cancel·lar",
    es = u"Cancelar",
    en = u"Cancel"
)

translations.define("Select",
    ca = u"Seleccionar",
    es = u"Seleccionar",
    en = u"Select"
)

translations.define("Submit",
    ca = u"Confirmar",
    es = u"Confirmar",
    en = u"Submit",
    pt = u"Enviar",
    de = u"Abschicken",
    pl = u"Zatwierdź",
    nl = u"Bevestig"
)

translations.define("Item count",
    ca = lambda page_range, item_count: \
        u"<strong>%d-%d</strong> de %d" % (
            page_range[0], page_range[1], item_count
        ),
    es = lambda page_range, item_count: \
        u"<strong>%d-%d</strong> de %d" % (
            page_range[0], page_range[1], item_count
        ),
    en = lambda page_range, item_count: \
        u"<strong>%d-%d</strong> of %d" % (
            page_range[0], page_range[1], item_count
        )
)

translations.define("Results per page",
    ca = u"Resultats per pàgina",
    es = u"Resultados por página",
    en = u"Results per page"
)

translations.define("cocktail.html.CollectionView no search results",
    ca = u"La cerca no conté cap element.",
    es = u"La búsqueda no contiene ningún elemento.",
    en = u"The search has no matches."
)

translations.define("cocktail.html.CollectionView no results",
    ca = u"La vista activa no conté cap element.",
    es = u"La vista activa no contiene ningún elemento.",
    en = u"The current view has no matching items."
)

translations.define("cocktail.html.CollectionView.members_dropdown",
    ca = u"Camps",
    es = u"Campos",
    en = u"Fields"
)

translations.define("cocktail.html.CollectionView.members_dropdown.shortcut",
    ca = u"c",
    es = u"c",
    en = u"f"
)

translations.define("cocktail.html.CollectionView.languages_dropdown",
    ca = u"Idiomes",
    es = u"Idiomas",
    en = u"Languages"
)

translations.define("cocktail.html.CollectionView.languages_dropdown.shortcut",
    ca = u"i",
    es = u"i",
    en = u"l"
)

translations.define("cocktail.page_size",
    ca = u"%(page_size)d resultats per pàgina",
    es = u"%(page_size)d resultados por pàgina",
    en = u"%(page_size)d results per page"
)

translations.define("Filters",
    ca = u"Filtres",
    es = u"Filtros",
    en = u"Filters"
)

translations.define(
    "cocktail.controllers.Location.client_redirect_title",
    ca = u"Redirecció",
    es = u"Redirección",
    en = u"Redirecting"
)

translations.define(
    "cocktail.controllers.Location.client_redirect_explanation",
    ca = u"S'està redirigint la petició. Si no ets automàticament redirigit, "
         u"prem %(control)s per continuar navegant pel web.",
    es = u"Se está redirigiendo la petición. Si no eres automáticamente "
         u"redirigido pulsa %(control)s para proseguir con la navegación.",
    en = u"Redirection in process. If you aren't redirected automatically "
         u"press %(control)s to proceed."
)

translations.define(
    "cocktail.controllers.Location.client_redirect_control-GET",
    ca = u"el botó",
    es = u"el botón",
    en = u"the button"
)

translations.define(
    "cocktail.controllers.Location.client_redirect_control-POST",
    ca = u"l'enllaç",
    es = u"el enlace",
    en = u"the link"
)

translations.define(
    "cocktail.controllers.Location.client_redirect_control",
    ca = u"Continuar",
    es = u"Continuar",
    en = u"Continue"
)

translations.define("cocktail.html.CollectionView search",
    ca = u"Cerca",
    es = u"Búsqueda",
    en = u"Search"
)

translations.define("cocktail.html.ContentView search results",
    ca = u"Resultats de la cerca:",
    es = u"Resultados de la búsqueda:",
    en = u"Search results:"
)

translations.define("cocktail.html.CollectionView selection options",
    ca = u"Seleccionar:",
    es = u"Seleccionar:",
    en = u"Select:"
)

translations.define("cocktail.html.CollectionView select all",
    ca = u"Tots",
    es = u"Todos",
    en = u"All"
)

translations.define("cocktail.html.CollectionView clear selection",
    ca = u"Cap",
    es = u"Ninguno",
    en = u"None"
)

translations.define("cocktail.html.modal_selector accept button",
    ca = u"Acceptar",
    es = u"Aceptar",
    en = u"Accept"
)

translations.define("cocktail.html.modal_selector cancel button",
    ca = u"Cancel·lar",
    es = u"Cancelar",
    en = u"Cancel"
)

translations.define("cocktail.html.modal_selector select button",
    ca = u"Seleccionar",
    es = u"Seleccionar",
    en = u"Select"
)

translations.define("Translations",
    ca = u"Traduccions",
    es = u"Traducciones",
    en = u"Translations"
)

translations.define("date format",
    ca = "%d/%m/%Y",
    es = "%d/%m/%Y",
    en = "%m/%d/%Y",
    de = "%d/%m/%Y",
    fr = "%d/%m/%Y",
    pt = "%d/%m/%Y"
)

translations.define("jquery_date format",
    ca = "dd/mm/yy",
    es = "dd/mm/yy",
    en = "mm/dd/yy"
)

# -------- ABBREVIATED TRANSLATIONS OF MONTHS
translations.define("month 1 abbr",
    ca = u"Gen",
    es = u"Ene",
    en = u"Jan",
    pt = u"Jan"
)

translations.define("month 2 abbr",
    ca = u"Feb",
    es = u"Feb",
    en = u"Feb",
    pt = u"Fev"
)

translations.define("month 3 abbr",
    ca = u"Mar",
    es = u"Mar",
    en = u"Mar",
    pt = u"Mar"
)

translations.define("month 4 abbr",
    ca = u"Abr",
    es = u"Abr",
    en = u"Apr",
    pt = u"Abr"
)

translations.define("month 5 abbr",
    ca = u"Mai",
    es = u"May",
    en = u"May",
    pt = u"Mai"
)

translations.define("month 6 abbr",
    ca = u"Jun",
    es = u"Jun",
    en = u"Jun",
    pt = u"Jun"
)

translations.define("month 7 abbr",
    ca = u"Jul",
    es = u"Jul",
    en = u"Jul",
    pt = u"Jul"
)

translations.define("month 8 abbr",
    ca = u"Ago",
    es = u"Ago",
    en = u"Aug",
    pt = u"Ago"
)

translations.define("month 9 abbr",
    ca = u"Set",
    es = u"Sep",
    en = u"Sep",
    pt = u"Set"
)

translations.define("month 10 abbr",
    ca = u"Oct",
    es = u"Oct",
    en = u"Oct",
    pt = u"Out"
)

translations.define("month 11 abbr",
    ca = u"Nov",
    es = u"Nov",
    en = u"Nov",
    pt = u"Nov"
)

translations.define("month 12 abbr",
    ca = u"Des",
    es = u"Dic",
    en = u"Dec",
    pt = u"Dez"
)

# -------- FULLTEXT TRANSLATIONS OF MONTHS
translations.define("month 1",
    ca = u"Gener",
    es = u"Enero",
    en = u"January",
    pt = u"Janeiro",
    de = u"Januar",
    pl = u"Styczeń",
    nl = u"januari"
)

translations.define("month 2",
    ca = u"Febrer",
    es = u"Febrero",
    en = u"February",
    pt = u"Fevereiro",
    de = u"Februar",
    pl = u"Luty",
    nl = u"februari"
)

translations.define("month 3",
    ca = u"Març",
    es = u"Marzo",
    en = u"March",
    pt = u"Março",
    de = u"März",
    pl = u"Marzec",
    nl = u"maart"
)

translations.define("month 4",
    ca = u"Abril",
    es = u"Abril",
    en = u"April",
    pt = u"Abril",
    de = u"April",
    pl = u"Kwiecień",
    nl = u"april"
)

translations.define("month 5",
    ca = u"Maig",
    es = u"Mayo",
    en = u"May",
    pt = u"Maio",
    de = u"Mai",
    pl = u"Maj",
    nl = u"mei"
)

translations.define("month 6",
    ca = u"Juny",
    es = u"Junio",
    en = u"June",
    pt = u"Junho",
    de = u"Juni",
    pl = u"Czerwiec",
    nl = u"juni"
)

translations.define("month 7",
    ca = u"Juliol",
    es = u"Julio",
    en = u"July",
    pt = u"Julho",
    de = u"Juli",
    pl = u"Lipiec",
    nl = u"juli"
)

translations.define("month 8",
    ca = u"Agost",
    es = u"Agosto",
    en = u"August",
    pt = u"Agosto",
    de = u"August",
    pl = u"Sierpień",
    nl = u"augustus"
)

translations.define("month 9",
    ca = u"Setembre",
    es = u"Septiembre",
    en = u"September",
    pt = u"Setembro",
    de = u"September",
    pl = u"Wrzesień",
    nl = u"september"
)

translations.define("month 10",
    ca = u"Octubre",
    es = u"Octubre",
    en = u"October",
    pt = u"Outubro",
    de = u"Oktober",
    pl = u"Październik",
    nl = u"oktober"
)

translations.define("month 11",
    ca = u"Novembre",
    es = u"Noviembre",
    en = u"November",
    pt = u"Novembro",
    de = u"November",
    pl = u"Listopad",
    nl = u"november"
)

translations.define("month 12",
    ca = u"Desembre",
    es = u"Diciembre",
    en = u"December",
    pt = u"Dezembro",
    de = u"Dezember",
    pl = u"Grudzień",
    nl = u"december"
)

# -------- ABBREVIATED TRANSLATIONS OF WEEKDAYS
translations.define("weekday 0 abbr", ca = u"Dl", es = u"Lun", en = u"Mon")
translations.define("weekday 1 abbr", ca = u"Dt", es = u"Mar", en = u"Tue")
translations.define("weekday 2 abbr", ca = u"Dc", es = u"Mié", en = u"Wed")
translations.define("weekday 3 abbr", ca = u"Dj", es = u"Jue", en = u"Thu")
translations.define("weekday 4 abbr", ca = u"Dv", es = u"Vie", en = u"Fri")
translations.define("weekday 5 abbr", ca = u"Ds", es = u"Sáb", en = u"Sat")
translations.define("weekday 6 abbr", ca = u"Dg", es = u"Dom", en = u"Sun")

# -------- FULLTEXT TRANSLATIONS OF WEEKDAYS
translations.define("weekday 0", ca = u"Dilluns", es = u"Lunes", en = u"Monday")
translations.define("weekday 1", ca = u"Dimarts", es = u"Martes", en = u"Tuesday")
translations.define("weekday 2", ca = u"Dimecres", es = u"Miércoles", en = u"Wednesday")
translations.define("weekday 3", ca = u"Dijous", es = u"Jueves", en = u"Thursday")
translations.define("weekday 4", ca = u"Divendres", es = u"Viernes", en = u"Friday")
translations.define("weekday 5", ca = u"Dissabte", es = u"Sábado", en = u"Saturday")
translations.define("weekday 6", ca = u"Diumenge", es = u"Domingo", en = u"Sunday")

translations.define("today",
    ca = u"Avui",
    es = u"Hoy",
    en = u"Today"
)

DATE_STYLE_NUMBERS = 1
DATE_STYLE_ABBR = 2
DATE_STYLE_TEXT = 3

def _date_instance_ca(instance, style = DATE_STYLE_NUMBERS, relative = False):

    if relative:
        today = date.today()
        date_value = (
            instance.date() if isinstance(instance, datetime) else instance
        )
        day_diff = (date_value - today).days

        if day_diff == 0:
            return u"Avui"
        elif day_diff == -1:
            return u"Ahir"
        elif day_diff == 1:
            return u"Demà"
        elif 1 < day_diff <= 7:
            return (
                translations("weekday %d" % instance.weekday())
                + u" que ve"
            )
        elif -7 <= day_diff < 0:
            return (
                translations("weekday %d" % instance.weekday())
                + u" passat"
            )

    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("date format"))
    elif style == DATE_STYLE_ABBR:
        desc = u"%s %s" % (
            instance.day,
            translations(u"month %s abbr" % instance.month)
        )
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc
    elif style == DATE_STYLE_TEXT:
        desc = u"%s %s" % (
            instance.day,
            ca_possessive(translations(u"month %s" % instance.month).lower())
        )
        if not relative or today.year != instance.year:
            desc += u" de %d" % instance.year
        return desc

def _date_instance_es(instance, style = DATE_STYLE_NUMBERS, relative = False):

    if relative:
        today = date.today()
        date_value = (
            instance.date() if isinstance(instance, datetime) else instance
        )
        day_diff = (date_value - today).days

        if day_diff == 0:
            return u"Hoy"
        elif day_diff == -1:
            return u"Ayer"
        elif day_diff == 1:
            return u"Mañana"
        elif 1 < day_diff <= 7:
            return (
                translations("weekday %d" % instance.weekday())
                + u" que viene"
            )
        elif -7 <= day_diff < 0:
            return (
                translations("weekday %d" % instance.weekday())
                + u" pasado"
            )

    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("date format"))
    elif style == DATE_STYLE_ABBR:
        desc = u"%s %s" % (
            instance.day,
            translations(u"month %s abbr" % instance.month)
        )
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc
    elif style == DATE_STYLE_TEXT:
        desc = u"%s de %s" % (
            instance.day,
            translations(u"month %s" % instance.month).lower()
        )
        if not relative or today.year != instance.year:
            desc += u" de %d" % instance.year
        return desc

def _date_instance_en(instance, style = DATE_STYLE_NUMBERS, relative = False):

    if relative:
        today = date.today()
        date_value = (
            instance.date() if isinstance(instance, datetime) else instance
        )
        day_diff = (date_value - today).days

        if day_diff == 0:
            return u"Today"
        elif day_diff == -1:
            return u"Yesterday"
        elif day_diff == 1:
            return u"Tomorrow"
        elif 1 < day_diff <= 7:
            return (
                u"Next "
                + translations("weekday %d" % instance.weekday()).lower()
            )
        elif -7 <= day_diff < 0:
            return (
                u"Past "
                + translations("weekday %d" % instance.weekday()).lower()
            )

    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("date format"))
    elif style == DATE_STYLE_ABBR:
        desc = u"%s %s" % (
            translations(u"month %s abbr" % instance.month),
            instance.day
        )
        if not relative or today.year != instance.year:
            desc += u" %d" % instance.year
        return desc
    elif style == DATE_STYLE_TEXT:
        desc = u"%s %s" % (
            translations(u"month %s" % instance.month),
            instance.day
        )
        if not relative or today.year != instance.year:
            desc += u", %d" % instance.year
        return desc

def _date_instance_pt(instance, style = DATE_STYLE_NUMBERS, relative = False):
    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("date format"))
    elif style == DATE_STYLE_ABBR:
        return u"%s %s %s" % (
            instance.day,
            translations(u"month %s abbr" % instance.month),
            instance.year
        )
    elif style == DATE_STYLE_TEXT:
        return u"%s de %s de %s" % (
            instance.day,
            translations(u"month %s" % instance.month).lower(),
            instance.year
        )

translations.define("datetime.date-instance",
    ca = _date_instance_ca,
    es = _date_instance_es,
    en = _date_instance_en,
    pt = _date_instance_pt
)

def _translate_time(value, include_seconds = True):
    return value.strftime("%H:%M" + (":%S" if include_seconds else ""))

translations.define("datetime.datetime-instance",
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
    pt = lambda instance, style = DATE_STYLE_NUMBERS, include_seconds = True:
        _date_instance_pt(instance, style)
        + u" " + _translate_time(instance, include_seconds)
)

translations.define("datetime.time-instance",
    ca = lambda instance, include_seconds = True:
         _translate_time(instance, include_seconds),
    es = lambda instance, include_seconds = True:
         _translate_time(instance, include_seconds),
    en = lambda instance, include_seconds = True:
         _translate_time(instance, include_seconds),
    pt = lambda instance, include_seconds = True:
         _translate_time(instance, include_seconds)
)

def _translate_calendar_page(instance, abbreviated = False):
    return "%s %d" % (
        translations(
            "month %d%s" % (
                instance[1],
                " abbr" if abbreviated else ""
            )
        ),
        instance[0]
    )

translations.define("cocktail.dateutils.CalendarPage-instance",
    ca = _translate_calendar_page,
    es = _translate_calendar_page,
    en = _translate_calendar_page
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

translations.define("time span",
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
            ca_possessive(translations("month %d" % start.month)),
            end.day,
            ca_possessive(translations("month %d" % end.month)),
            start.year
        )
    else:
        return u"Del %d al %d %s de %d" % (
            start.day,
            end.day,
            ca_possessive(translations("month %d" % start.month)),
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
            translations("month %d" % start.month),
            end.day,
            translations("month %d" % end.month),
            start.year
        )
    else:
        return u"Del %d al %d de %s de %d" % (
            start.day,
            end.day,
            translations("month %d" % start.month),
            start.year
        )

translations.define("ordinal",
    en = lambda number:
        str(number)
        + {1: 'st', 2: 'nd', 3: 'rd'}
          .get(number % (10 < number % 100 < 14 or 10), 'th')
)


def _date_range_en(start, end):
    if start.year != end.year:
        return u"From %s until %s" % (
            translations(start, style = DATE_STYLE_TEXT),
            translations(end, style = DATE_STYLE_TEXT)
        )
    elif start.month != end.month:
        return u"From the %s of %s until the %s of %s %d" % (
            translations("ordinal", number = start.day),
            translations("month %d" % start.month),
            translations("ordinal", number = end.day),
            translations("month %d" % end.month),
            start.year
        )
    else:
        return u"From the %s until the %s of %s %d" % (
            translations("ordinal", number = start.day),
            translations("ordinal", number = end.day),
            translations("month %d" % start.month),
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
            translations("month %d" % start.month),
            end.day,
            translations("month %d" % end.month),
            start.year
        )
    else:
        return u"De %d a %d de %s de %d" % (
            start.day,
            end.day,
            translations("month %d" % start.month),
            start.year
        )

translations.define("date range",
    ca = _date_range_ca,
    es = _date_range_es,
    en = _date_range_en,
    pt = _date_range_pt
)

# html.FilterBox
#------------------------------------------------------------------------------
translations.define("cocktail.html.FilterBox add filter",
    ca = u"Afegir filtre",
    es = u"Añadir filtro",
    en = u"Add filter"
)

translations.define("cocktail.html.FilterBox remove filters",
    ca = u"Treure filtres",
    es = u"Quitar filtros",
    en = u"Remove filters"
)

translations.define("cocktail.html.FilterBox.delete_button",
    ca = u"Treure el filtre",
    es = u"Quitar el filtro",
    en = u"Remove this filter"
)

translations.define("cocktail.html.FilterBox discard filters",
    ca = u"Descartar",
    es = u"Descartar",
    en = u"Discard"
)

translations.define("cocktail.html.FilterBox apply filters",
    ca = u"Cercar",
    es = u"Buscar",
    en = u"Search"
)

translations.define("cocktail.html.UserFilterEntry operator eq",
    ca = u"Igual a",
    es = u"Igual a",
    en = u"Equals"
)

translations.define("cocktail.html.UserFilterEntry operator ne",
    ca = u"Diferent de",
    es = u"Distinto de",
    en = u"Not equals"
)

translations.define("cocktail.html.UserFilterEntry operator gt",
    ca = u"Major que",
    es = u"Mayor que",
    en = u"Greater than"
)

translations.define("cocktail.html.UserFilterEntry operator ge",
    ca = u"Major o igual que",
    es = u"Mayor o igual que",
    en = u"Greater or equal than"
)

translations.define("cocktail.html.UserFilterEntry operator lt",
    ca = u"Menor que",
    es = u"Menor que",
    en = u"Lower than"
)

translations.define("cocktail.html.UserFilterEntry operator le",
    ca = u"Menor o igual que",
    es = u"Menor o igual que",
    en = u"Lower or equal than"
)

translations.define("cocktail.html.UserFilterEntry operator sr",
    ca = u"Conté",
    es = u"Contiene",
    en = u"Contains"
)

translations.define("cocktail.html.UserFilterEntry operator sw",
    ca = u"Comença per",
    es = u"Empieza por",
    en = u"Starts with"
)

translations.define("cocktail.html.UserFilterEntry operator ew",
    ca = u"Acaba en",
    es = u"Acaba en",
    en = u"Ends with"
)

translations.define("cocktail.html.UserFilterEntry operator re",
    ca = u"Coincideix amb l'expressió regular",
    es = u"Coincide con la expresión regular",
    en = u"Matches regular expression"
)

translations.define("cocktail.html.UserFilterEntry operator cn",
    ca = u"Conté",
    es = u"Contiene",
    en = u"Contains"
)

translations.define("cocktail.html.UserFilterEntry operator nc",
    ca = u"No conté",
    es = u"No contiene",
    en = u"Doesn't contain"
)

translations.define("UserFilter.language",
    ca = u"en",
    es = u"en",
    en = u"in"
)

translations.define("cocktail.html.UserFilterEntry any language",
    ca = u"en qualsevol idioma",
    es = u"en cualquier idioma",
    en = u"in any language"
)

translations.define("cocktail.controllers.userfilter.GlobalSearchFilter-instance",
    ca = u"Conté les paraules",
    es = u"Contiene las palabras",
    en = u"Has the words"
)

translations.define(
    "cocktail.controllers.userfilter.DateTimeRangeFilter-instance",
    ca = u"Rang de dates",
    es = u"Rango de fechas",
    en = u"Date range"
)

translations.define(
    "DateTimeRangeFilter.start_date",
    ca = u"Des de",
    es = u"Desde",
    en = u"From"
)

translations.define(
   "DateTimeRangeFilter.end_date",
    ca = u"Fins a",
    es = u"Hasta",
    en = u"Until"
)

translations.define(
    "cocktail.controllers.userfilter.DescendsFromFilter-instance",
    ca = u"Descendència",
    es = u"Descendencia",
    en = u"Descendancy"
)

translations.define("DescendsFromFilter.include_self",
    ca = u"Arrel inclosa",
    es = u"Raíz incluida",
    en = u"Root included"
)

# Languages
#------------------------------------------------------------------------------
def _translate_locale(locale):

    trans = translations(locale)
    if trans:
        return trans

    return u"".join(
        translations("locale_component." + component,
            locale = locale,
            index = index
        )
        or translations("locale_component",
            locale = locale,
            component = component,
            index = index
        )
        or (u" - " if index else u"") + component
        for index, component in enumerate(locale.split("-"))
    )

def translate_locale_component(locale, component, index):
    if index == 0:
        return translations(component)

translations.define("locale", **dict(
    (lang, _translate_locale)
    for lang in (
        "ca",
        "cn",
        "de",
        "en",
        "es",
        "fr",
        "it",
        "jp",
        "ko",
        "nl",
        "pl",
        "pt",
        "ru",
        "tr"
    )
))

translations.define("locale_component", **dict(
    (lang, translate_locale_component)
    for lang in (
        "ca",
        "cn",
        "de",
        "en",
        "es",
        "fr",
        "it",
        "jp",
        "ko",
        "nl",
        "pl",
        "pt",
        "ru",
        "tr"
    )
))

translations.define("ca",
    ca = u"Català",
    es = u"Catalán",
    en = u"Catalan"
)

translations.define("es",
    ca = u"Castellà",
    es = u"Español",
    en = u"Spanish"
)

translations.define("en",
    ca = u"Anglès",
    es = u"Inglés",
    en = u"English"
)

translations.define("fr",
    ca = u"Francès",
    es = u"Francés",
    en = u"French",
    fr = u"Français"
)

translations.define("de",
    ca = u"Alemany",
    es = u"Alemán",
    en = u"German",
    de = u"Deutsch"
)

translations.define("pt",
    ca = u"Portuguès",
    es = u"Portugués",
    en = u"Portuguese",
    pt = u"Português"
)

translations.define("it",
    ca = u"Italià",
    es = u"Italiano",
    en = u"Italian",
    it = u"Italiano"
)

translations.define("ru",
    ca = u"Rus",
    es = u"Ruso",
    en = u"Russian",
    ru = u"Ру́сский язы́к"
)

translations.define("pl",
    ca = u"Polac",
    es = u"Polaco",
    en = u"Polish",
    pl = u"Polski"
)

translations.define("nl",
    ca = u"Holandès",
    es = u"Holandés",
    en = u"Dutch",
    nl = u"Nederlands"
)

translations.define("tr",
    ca = u"Turc",
    es = u"Turco",
    en = u"Turkish",
    tr = u"Türkçe"
)

translations.define("ko",
    ca = u"Coreà",
    es = u"Coreano",
    en = u"Korean",
    ko = u"Hanguk"
)

translations.define("ja",
    ca = u"Japonès",
    es = u"Japonés",
    en = u"Japanese",
    jp = u"日本語"
)

translations.define("zh",
    ca = u"Xinès",
    es = u"Chino",
    en = u"Chinese",
    cn = u"汉语"
)

translations.define("cs",
    ca = u"Txec",
    es = u"Checo",
    en = u"Czech"
)

translations.define("hu",
    ca = u"Húngar",
    es = u"Húngaro",
    en = u"Hungarian"
)

translations.define("el",
    ca = u"Grec",
    es = u"Griego",
    en = u"Greek"
)

translations.define("no",
    ca = u"Norueg",
    es = u"Noruego",
    en = u"Norwegian"
)

translations.define("sv",
    ca = u"Suec",
    es = u"Sueco",
    en = u"Swedish"
)

translations.define("ro",
    ca = u"Romanès",
    es = u"Rumano",
    en = u"Romanian"
)

translations.define("translated into",
    ca = lambda lang: "en " + translations("locale", locale = lang),
    es = lambda lang: "en " + translations("locale", locale = lang),
    en = lambda lang: "in " + translations("locale", locale = lang),
    fr = lambda lang: "en " + translations("locale", locale = lang),
    de = lambda lang: "auf " + translations("locale", locale = lang)
)

translations.define("cocktail.schema.Member qualified",
    ca = lambda member: u"%s %s" % (
            translations(member),
            ca_possessive(translations(member.schema.name).lower())
        ),
    es = lambda member: u"%s de %s" % (
            translations(member),
            translations(member.schema.name).lower()
        ),
    en = lambda member: u"%s %s" % (
            translations(member.schema.name),
            translations(member).lower()
        )
)

translations.define("Exception-instance",
    ca = lambda instance: u"Error inesperat (%s: %s)" %
        (instance.__class__.__name__, instance),
    es = lambda instance: u"Error inesperado (%s: %s)" %
        (instance.__class__.__name__, instance),
    en = lambda instance: u"Unexpected error (%s: %s)" %
        (instance.__class__.__name__, instance)
)

# Validation errors
#------------------------------------------------------------------------------
def member_identifier(error):

    from cocktail import schema

    path = list(error.context.path())
    desc = []

    for i, context in enumerate(path):
        if isinstance(context.member, schema.Schema) and (
            (i == 0 and len(path) > 1)
            or (
                context.parent_context
                and isinstance(
                    context.parent_context.member,
                    schema.RelationMember
                )
            )
        ):
            continue

        label = decapitalize(translations(context.member))

        if context.collection_index is not None:
            if isinstance(context.collection_index, int):
                label += u" %d" % (context.collection_index + 1)
            elif (
                context.parent_context
                and isinstance(context.parent_context.member, schema.Mapping)
                and context.parent_context.member.keys
            ):
                key_label = context.parent_context.member.keys.translate_value(
                    context.collection_index
                )
                if label:
                    if key_label:
                        label = u"%s: %s" % (key_label, label)
                else:
                    label = key_label
            else:
                label = u"%s: %s" % (context.collection_index, label)

        if error.language:
            label += u" (%s)" % (
                translations("locale", locale = error.language)
            )

        desc.append(label.strip())

    return u" » ".join(desc)

translations.define("cocktail.schema.exceptions.ValidationError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> no és vàlid"
        % member_identifier(instance),
    es = lambda instance:
        u"El campo <em>%s</em> no es válido"
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> field is not valid"
        % member_identifier(instance)
)

translations.define("cocktail.schema.exceptions.ValueRequiredError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> no pot estar buit"
        % member_identifier(instance),
    es = lambda instance:
        u"El campo <em>%s</em> no puede estar vacío"
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> field can't be empty"
        % member_identifier(instance),
    pt = lambda instance:
        u"O campo <em>%s</em> tem que ser preenchido"
        % member_identifier(instance),
    de = lambda instance:
        u"Das Feld <em>%s</em> muss ausgefüllt werden"
        % member_identifier(instance),
)

translations.define("cocktail.schema.exceptions.NoneRequiredError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha d'estar buit"
        % member_identifier(instance),
    es = lambda instance:
        u"El campo <em>%s</em> debe estar vacío"
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> field must be empty"
        % member_identifier(instance)
)

translations.define("cocktail.schema.exceptions.TypeCheckError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> té un tipus incorrecte"
        % member_identifier(instance),
    es = lambda instance:
        u"El campo <em>%s</em> tiene un tipo incorrecto"
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> field is of the wrong type"
        % member_identifier(instance)
)

translations.define("cocktail.schema.exceptions.EnumerationError-instance",
    ca = lambda instance:
        u"El valor del camp <em>%s</em> no és un dels permesos"
        % member_identifier(instance),
    es = lambda instance:
        u"El campo <em>%s</em> no es uno de los permitidos"
        % member_identifier(instance),
    en = lambda instance:
        u"Wrong choice on field <em>%s</em>"
        % member_identifier(instance)
)

translations.define("cocktail.schema.exceptions.MinLengthError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de tenir un mínim de %d caràcters"
        % (member_identifier(instance), instance.min),
    es = lambda instance:
        u"El campo <em>%s</em> debe tener un mínimo de %d caracteres"
        % (member_identifier(instance), instance.min),
    en = lambda instance:
        u"The <em>%s</em> field must be at least %d characters long"
        % (member_identifier(instance), instance.min),
    pt = lambda instance:
        u"O campo <em>%s</em> deve ter pelo menos %d caracteres"
        % (member_identifier(instance), instance.min)
)

translations.define("cocktail.schema.exceptions.MaxLengthError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de tenir un màxim de %d caràcters"
        % (member_identifier(instance), instance.max),
    es = lambda instance:
        u"El campo <em>%s</em> debe tener un máximo de %d caracteres"
        % (member_identifier(instance), instance.max),
    en = lambda instance:
        u"The <em>%s</em> field can't be more than %d characters long"
        % (member_identifier(instance), instance.max),
    pt = lambda instance:
        u"O campo <em>%s</em> deve ter um máximo de %d caracteres"
        % (member_identifier(instance), instance.max)
)

translations.define("cocktail.schema.exceptions.FormatError-instance",
    ca = lambda instance:
        u"El format del camp <em>%s</em> és incorrecte"
        % member_identifier(instance),
    es = lambda instance:
        u"El formato del campo <em>%s</em> es incorrecto"
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> field has a wrong format"
        % member_identifier(instance),
    de = lambda instance:
        u"Das Feld <em>%s</em> hat ein falsches Format"
        % member_identifier(instance),
    pt = lambda instance:
        u"O formato do campo <em>%s</em> é incorreto"
        % member_identifier(instance)
)

translations.define(
    "cocktail.schema.exceptions.PhoneFormatError-instance",
    ca = lambda instance:
        u"El valor indicat pel camp <em>%s</em> no és un número de telèfon "
        u"vàlid."
        % member_identifier(instance),
    es = lambda instance:
        u"El valor indicado para el campo <em>%s</em> no es un número de "
        u"teléfono válido."
        % member_identifier(instance),
    en = lambda instance:
        u"The value for the <em>%s</em> field is not a valid phone number."
        % member_identifier(instance)
)

translations.define(
    "cocktail.schema.exceptions.InternationalPhoneNumbersNotAllowedError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> conté un telèfon internacional: només "
        u"s'accepten números locals."
        % member_identifier(instance),
    es = lambda instance:
        u"El campo <em>%s</em> contiene un teléfono internacional: solo "
        u"se aceptan números locales."
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> field only allows local phone numbers."
        % member_identifier(instance)
)

translations.define(
    "cocktail.schema.exceptions.InvalidPhoneCountryError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> no accepta números del país indicat."
        % member_identifier(instance),
    es = lambda instance:
        u"El campo <em>%s</em> no acepta números del país indicado."
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> field doesn't allow numbers from the indicated "
        u"country."
        % member_identifier(instance)
)

translations.define("cocktail.schema.exceptions.MinValueError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de ser igual o superior a %s"
        % (
            member_identifier(instance),
            instance.member.translate_value(instance.max)
        ),
    es = lambda instance:
        u"El campo <em>%s</em> debe ser igual o superior a %s"
        % (
            member_identifier(instance),
            instance.member.translate_value(instance.max)
        ),
    en = lambda instance:
        u"The <em>%s</em> field must be greater or equal than %s"
        % (
            member_identifier(instance),
            instance.member.translate_value(instance.max)
        )
)

translations.define("cocktail.schema.exceptions.MaxValueError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de ser igual o inferior a %s"
        % (
            member_identifier(instance),
            instance.member.translate_value(instance.max)
        ),
    es = lambda instance:
        u"El campo <em>%s</em> debe ser igual o inferior a %s"
        % (
            member_identifier(instance),
            instance.member.translate_value(instance.max)
        ),
    en = lambda instance:
        u"The <em>%s</em> field must be lower or equal than %s"
        % (
            member_identifier(instance),
            instance.member.translate_value(instance.max)
        )
)

translations.define("cocktail.schema.exceptions.MinItemsError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de contenir %d o més elements"
        % (member_identifier(instance), instance.min),
    es = lambda instance:
        u"El campo <em>%s</em> debe contener %d o más elementos"
        % (member_identifier(instance), instance.min),
    en = lambda instance:
        u"The <em>%s</em> field must contain %d or more items"
        % (member_identifier(instance), instance.min)
)

translations.define("cocktail.schema.exceptions.MaxItemsError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> no pot contenir més de %d elements"
        % (member_identifier(instance), instance.max),
    es = lambda instance:
        u"El campo <em>%s</em> no puede contener más de %d elementos"
        % (member_identifier(instance), instance.max),
    en = lambda instance:
        u"The <em>%s</em> field can't contain more than %d items"
        % (member_identifier(instance), instance.max)
)

translations.define(
    "cocktail.schema.exceptions.CreditCardChecksumError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> té un dígit de control incorrecte"
        % member_identifier(instance),
    es = lambda instance:
        u"El camp <em>%s</em> tiene un dígito de control incorrecto"
        % member_identifier(instance),
    en = lambda instance:
        u"The <em>%s</em> field has an invalid control digit"
        % member_identifier(instance)
)

translations.define(
    "cocktail.persistence.persistentobject.UniqueValueError-instance",
    ca = lambda instance:
        u"El valor indicat pel camp <em>%s</em> ja existeix a la base de dades"
        % member_identifier(instance),
    es = lambda instance:
        u"El valor indicado para el campo <em>%s</em> ya existe en la base de "
        u"datos"
        % member_identifier(instance),
    en = lambda instance:
        u"The value of the <em>%s</em> field is already in use"
        % member_identifier(instance)
)

translations.define(
    "cocktail.unexpected_error",
    ca = lambda error:
        u"Error inesperat %s"
        %(error),
    es = lambda error:
        u"Error inesperado %s"
        %(error),
    en = lambda error:
        u"Unexpedted error %s"
        %(error)
)

translations.define(
    "cocktail.controllers.imageupload.ImageTooSmallError-instance",
    ca = lambda instance:
        u"El fitxer proporcionat pel camp <em>%s</em> és massa petit: la mida "
        u"mínima permesa és de %sx%s pixels" % (
            member_identifier(instance),
            instance.min_width or u"∞",
            instance.min_height or u"∞"
        ),
    es = lambda instance:
        u"El fichero proporcionado para el campo <em>%s</em> es demasiado "
        u"pequeño: el tamaño mínimo permitido es de %sx%s píxeles" % (
            member_identifier(instance),
            instance.min_width or u"∞",
            instance.min_height or u"∞"
        ),
    en = lambda instance:
        u"The file given in field <em>%s</em> is too small: the minimum allowed "
        u"size is %sx%s pixels"  % (
            member_identifier(instance),
            instance.min_width or u"∞",
            instance.min_height or u"∞"
        )
)

translations.define(
    "cocktail.controllers.imageupload.ImageTooBigError-instance",
    ca = lambda instance:
        u"El fitxer proporcionat pel camp <em>%s</em> és massa gran: la mida "
        u"màxima permesa és de %sx%s pixels" % (
            member_identifier(instance),
            instance.max_width or u"∞",
            instance.max_height or u"∞"
        ),
    es = lambda instance:
        u"El fichero proporcionado para el campo <em>%s</em> es demasiado "
        u"grande: el tamaño máximo permitido es de %sx%s píxeles" % (
            member_identifier(instance),
            instance.max_width or u"∞",
            instance.max_height or u"∞"
        ),
    en = lambda instance:
        u"The file given in field <em>%s</em> is too big: the maximum allowed "
        u"size is %sx%s pixels"  % (
            member_identifier(instance),
            instance.max_width or u"∞",
            instance.max_height or u"∞"
        )
)

# Value parsing
#------------------------------------------------------------------------------

def _thousands_parser(thousands_sep, fraction_sep):

    expr = re.compile(r"^[-+]?((\d{1,3}(\%s\d{3})*)|\d+)(\%s\d+)?$"
                    % (thousands_sep, fraction_sep))

    def parser(value):

        if not expr.match(value):
            raise ValueError("Invalid decimal literal: %s" % value)

        value = value.replace(thousands_sep, "")

        if fraction_sep != ".":
            value = value.replace(fraction_sep, ".")

        return Decimal(value)

    return parser

def _serialize_thousands(value, thousands_sep, fraction_sep):

    sign, num, precision = value.as_tuple()
    num = list(num)
    if abs(precision) > len(num):
        num = [0] * (abs(precision) - len(num)) + num
    pos = len(num) + precision
    integer = num[:pos]
    fraction = num[pos:]

    blocks = []

    while integer:
        blocks.insert(0, "".join(str(i) for i in integer[-3:]))
        integer = integer[:-3]

    if blocks:
        serialized_value = thousands_sep.join(blocks)
    else:
        serialized_value = "0"

    if fraction:
        serialized_value += fraction_sep \
                          + str("".join(str(i) for i in fraction))

    if sign:
        serialized_value = "-" + serialized_value

    return serialized_value

translations.define("Decimal parser",
    ca = lambda: _thousands_parser(".", ","),
    es = lambda: _thousands_parser(".", ","),
    en = lambda: _thousands_parser(",", "."),
    de = lambda: _thousands_parser(".", ","),
    fr = lambda: _thousands_parser(".", ","),
    pt = lambda: _thousands_parser(".", ",")
)

translations.define("decimal.Decimal-instance",
    ca = lambda instance: _serialize_thousands(instance, ".", ","),
    es = lambda instance: _serialize_thousands(instance, ".", ","),
    en = lambda instance: _serialize_thousands(instance, ",", "."),
    de = lambda instance: _serialize_thousands(instance, ".", ","),
    fr = lambda instance: _serialize_thousands(instance, ".", ","),
    pt = lambda instance: _serialize_thousands(instance, ".", ",")
)

# Grouping
#------------------------------------------------------------------------------
translations.define("cocktail.controllers.grouping.MemberGrouping-ascending",
    ca = u"Ascendent",
    es = u"Ascendiente",
    en = u"Ascending"
)

translations.define("cocktail.controllers.grouping.MemberGrouping-descending",
    ca = u"Descendent",
    es = u"Descendiente",
    en = u"Descending"
)

translations.define(
    "cocktail.controllers.grouping.MemberGrouping default variant",
    ca = u"Per valor",
    es = u"Por valor",
    en = u"By value"
)

translations.define("cocktail.controllers.grouping.DateGrouping year variant",
    ca = u"Per any",
    es = u"Por año",
    en = u"By year"
)

translations.define("cocktail.controllers.grouping.DateGrouping month variant",
    ca = u"Per mes",
    es = u"Por mes",
    en = u"By month"
)

translations.define("cocktail.controllers.grouping.DateGrouping day variant",
    ca = u"Per dia",
    es = u"Por día",
    en = u"By day"
)

translations.define("cocktail.controllers.grouping.TimeGrouping hour variant",
    ca = u"Per hora",
    es = u"Por hora",
    en = u"By hour"
)

def _DateGrouping_value(grouping, value):
    if grouping.variant == "year":
        return value.year
    elif grouping.variant == "month":
        return "%s %d" % (translations("month %d" % value.month), value.year)
    else:
        return translations(value, style = DATE_STYLE_TEXT)

translations.define("cocktail.controllers.grouping.DateGrouping value",
    ca = _DateGrouping_value,
    es = _DateGrouping_value,
    en = _DateGrouping_value
)

# Date interval
#------------------------------------------------------------------------------
def _date_interval_ca(dates = None):
    start_date, end_date = dates

    date_string = ""

    def month_string(date, show = False):
        if date.month in (4, 8, 10):
            return  u"d'%s" % translations(u"month %s" % (date.month)) \
                if show else ""
        else:
            return  u"de %s" % translations(u"month %s" % (date.month)) \
                if show else ""

    def year_string(date, show = False):
        return " de %d" % (date.year,) if show else ""

    show_start_year = show_end_year = show_start_month = show_end_month = False

    if start_date.year != end_date.year:
        show_start_year = show_end_year = show_start_month = show_end_month = True
    elif start_date.month != end_date.month:
        show_end_year = end_date.year != datetime.now().year
        show_start_month = show_end_month = True
    else:
        show_end_year = end_date.year != datetime.now().year
        show_end_month = True

    # One day interval
    if start_date.day == end_date.day and \
        start_date.month == end_date.month and \
        start_date.year == end_date.year:

        date_string = "%d %s%s" % (
            start_date.day,
            month_string(start_date, True),
            year_string(
                start_date,
                show = start_date.year != datetime.now().year
            )
        )

    else:
        if start_date.day == 1:
            day_format = u"De l'%d "
        else:
            day_format = u"Del %d "

        date_string = day_format % (start_date.day,)

        if start_date.month == end_date.month \
            and start_date.year == end_date.year:

            date_string += "al %d %s%s" % (
                end_date.day,
                month_string(end_date, show_end_month),
                year_string(end_date, show_end_year)
            )

        else:
            date_string += "%s%s al %d %s%s" % (
                month_string(start_date, show_start_month),
                year_string(start_date, show_start_year),
                end_date.day,
                month_string(end_date, show_end_month),
                year_string(end_date, show_end_year)
            )

    return date_string

def _date_interval_es(dates = None):
    start_date, end_date = dates

    date_string = ""

    def month_string(date, show = False):
        return  u"de %s" % translations(u"month %s" % (date.month)) \
            if show else ""

    def year_string(date, show = False):
        return " de %d" % (date.year,) if show else ""

    show_start_year = show_end_year = show_start_month = show_end_month = False

    if start_date.year != end_date.year:
        show_start_year = show_end_year = show_start_month = show_end_month = True
    elif start_date.month != end_date.month:
        show_end_year = end_date.year != datetime.now().year
        show_start_month = show_end_month = True
    else:
        show_end_year = end_date.year != datetime.now().year
        show_end_month = True

    # One day interval
    if start_date.day == end_date.day and \
        start_date.month == end_date.month and \
        start_date.year == end_date.year:

        date_string = "%d %s%s" % (
            start_date.day,
            month_string(start_date, True),
            year_string(
                start_date,
                show = start_date.year != datetime.now().year
            )
        )

    else:
        date_string = u"Del %d " % (start_date.day,)

        if start_date.month == end_date.month \
            and start_date.year == end_date.year:

            date_string += "al %d %s%s" % (
                end_date.day,
                month_string(end_date, show_end_month),
                year_string(end_date, show_end_year)
            )

        else:
            date_string += "%s%s al %d %s %s" % (
                month_string(start_date, show_start_month),
                year_string(start_date, show_start_year),
                end_date.day,
                month_string(end_date, show_end_month),
                year_string(end_date, show_end_year)
            )

    return date_string

def _date_interval_en(dates = None):
    start_date, end_date = dates

    date_string = ""

    def month_string(date, show = False):
        return translations(u"month %s" % (date.month)) if show else ""

    def year_string(date, show = False):
        return ", %d" % (date.year,) if show else ""

    show_start_year = show_end_year = show_start_month = show_end_month = False

    if start_date.year != end_date.year:
        show_start_year = show_end_year = show_start_month = show_end_month = True
    elif start_date.month != end_date.month:
        show_end_year = end_date.year != datetime.now().year
        show_start_month = show_end_month = True
    else:
        show_end_year = end_date.year != datetime.now().year
        show_end_month = True

    # One day interval
    if start_date.day == end_date.day and \
        start_date.month == end_date.month and \
        start_date.year == end_date.year:

        date_string = "%d %s%s" % (
            start_date.day,
            month_string(start_date, True),
            year_string(
                start_date,
                show = start_date.year != datetime.now().year
            )
        )

    else:
        if start_date.month == end_date.month \
            and start_date.year == end_date.year:

            date_string += "From %s %d to %d%s" % (
                month_string(end_date, show_end_month),
                start_date.day,
                end_date.day,
                year_string(end_date, show_end_year)
            )

        else:
            date_string += "From %s %d%s to %s %d%s" % (
                month_string(start_date, show_start_month),
                start_date.day,
                year_string(start_date, show_start_year),
                month_string(end_date, show_end_month),
                end_date.day,
                year_string(end_date, show_end_year)
            )

    return date_string

translations.define("Date interval",
    ca = _date_interval_ca,
    es = _date_interval_es,
    en = _date_interval_en
)

# Expressions
#------------------------------------------------------------------------------
translations.define("cocktail.schema.expressions.SelfExpression-instance",
    ca = u"l'element avaluat",
    es = u"el elemento evaluado",
    en = u"the evaluated item"
)

def _op_translation_factory(format):
    def operation_translator(instance, **kwargs):
        if len(instance.operands) == 2 \
        and getattr(instance.operands[0], "translate_value", None) \
        and isinstance(instance.operands[1], Constant):
            operands = (
                translations(instance.operands[0], **kwargs),
                instance.operands[0].translate_value(
                    instance.operands[1].value,
                    **kwargs
                ) or u"Ø"
            )
        else:
            operands = tuple(
                translations(operand, **kwargs)
                for operand in instance.operands
            )

        return format % operands

    return operation_translator

translations.define("cocktail.schema.expressions.EqualExpression-instance",
    ca = _op_translation_factory(u"%s igual a %s"),
    es = _op_translation_factory(u"%s igual a %s"),
    en = _op_translation_factory(u"%s equals %s")
)

translations.define("cocktail.schema.expressions.NotEqualExpression-instance",
    ca = _op_translation_factory(u"%s diferent de %s"),
    es = _op_translation_factory(u"%s distinto de %s"),
    en = _op_translation_factory(u"%s not equals %s")
)

translations.define("cocktail.schema.expressions.GreaterExpression-instance",
    ca = _op_translation_factory(u"%s major que %s"),
    es = _op_translation_factory(u"%s mayor que %s"),
    en = _op_translation_factory(u"%s greater than %s")
)

translations.define(
    "cocktail.schema.expressions.GreaterEqualExpression-instance",
    ca = _op_translation_factory(u"%s major o igual que %s"),
    es = _op_translation_factory(u"%s mayor o igual que %s"),
    en = _op_translation_factory(u"%s greater or equal than %s")
)

translations.define("cocktail.schema.expressions.LowerExpression-instance",
    ca = _op_translation_factory(u"%s menor que %s"),
    es = _op_translation_factory(u"%s menor que %s"),
    en = _op_translation_factory(u"%s lower than %s")
)

translations.define(
    "cocktail.schema.expressions.LowerEqualExpression-instance",
    ca = _op_translation_factory(u"%s menor o igual que %s"),
    es = _op_translation_factory(u"%s menor o igual que %s"),
    en = _op_translation_factory(u"%s lower or equal than %s")
)

translations.define(
    "cocktail.schema.expressions.StartsWithExpression-instance",
    ca = _op_translation_factory(u"%s comença per %s"),
    es = _op_translation_factory(u"%s empieza por %s"),
    en = _op_translation_factory(u"%s starts with %s")
)

translations.define(
    "cocktail.schema.expressions.EndsWithExpression-instance",
    ca = _op_translation_factory(u"%s acaba per %s"),
    es = _op_translation_factory(u"%s acaba en %s"),
    en = _op_translation_factory(u"%s ends with %s")
)

translations.define(
    "cocktail.schema.expressions.ContainsExpression-instance",
    ca = _op_translation_factory(u"%s conté les paraules %s"),
    es = _op_translation_factory(u"%s contiene las palabras %s"),
    en = _op_translation_factory(u"%s contains search query %s")
)

translations.define(
    "cocktail.schema.expressions.GlobalSearchExpression-instance",
    ca = lambda instance:
        u"conté les paraules '"
        + instance.search_string
        + u"' en " + ca_either(map(translations, instance.languages)),
    es = lambda instance:
        u"contiene las palabras '"
        + instance.search_string
        + u"' en " + es_either(map(translations, instance.languages)),
    en = lambda instance:
        u"contains the words '"
        + instance.search_string
        + u"' in " + en_either(map(translations, instance.languages))
)

translations.define(
    "cocktail.schema.expressions.AddExpression-instance",
    ca = _op_translation_factory(u"%s mes %s"),
    es = _op_translation_factory(u"%s mas %s"),
    en = _op_translation_factory(u"%s plus %s")
)

translations.define(
    "cocktail.schema.expressions.SubtractExpression-instance",
    ca = _op_translation_factory(u"%s menys %s"),
    es = _op_translation_factory(u"%s menos %s"),
    en = _op_translation_factory(u"%s minus %s")
)

translations.define(
    "cocktail.schema.expressions.ProductExpression-instance",
    ca = _op_translation_factory(u"%s pers %s"),
    es = _op_translation_factory(u"%s por %s"),
    en = _op_translation_factory(u"%s multiplied by %s")
)

translations.define(
    "cocktail.schema.expressions.DivisionExpression-instance",
    ca = _op_translation_factory(u"%s entre %s"),
    es = _op_translation_factory(u"%s entre %s"),
    en = _op_translation_factory(u"%s divided by %s")
)

translations.define(
    "cocktail.schema.expressions.AndExpression-instance",
    ca = _op_translation_factory(u"%s i %s"),
    es = _op_translation_factory(u"%s y %s"),
    en = _op_translation_factory(u"%s and %s")
)

translations.define(
    "cocktail.schema.expressions.OrExpression-instance",
    ca = _op_translation_factory(u"%s o %s"),
    es = _op_translation_factory(u"%s o %s"),
    en = _op_translation_factory(u"%s or %s")
)

translations.define(
    "cocktail.schema.expressions.NotExpression-instance",
    ca = _op_translation_factory(u"no %s"),
    es = _op_translation_factory(u"no %s"),
    en = _op_translation_factory(u"not %s")
)

translations.define(
    "cocktail.schema.expressions.NegativeExpression-instance",
    ca = _op_translation_factory(u"-%s"),
    es = _op_translation_factory(u"-%s"),
    en = _op_translation_factory(u"-%s")
)

translations.define(
    "cocktail.schema.expressions.PositiveExpression-instance",
    ca = _op_translation_factory(u"+%s"),
    es = _op_translation_factory(u"+%s"),
    en = _op_translation_factory(u"+%s")
)

def _list_op_translation_factory(format, join):

    def list_op_translation(instance, **kwargs):
        rel = instance.operands[0]
        items = instance.operands[1]

        if isinstance(items, Constant):
            items = items.value

        item_translator = getattr(rel, "translate_value", translations)

        return format % (
            translations(rel, **kwargs),
            join(
                item_translator(item, **kwargs)
                for item in items
            )
        )

    return list_op_translation

translations.define(
    "cocktail.schema.expressions.InclusionExpression-instance",
    ca = _list_op_translation_factory(u"%s és %s", ca_either),
    es = _list_op_translation_factory(u"%s es %s", es_either),
    en = _list_op_translation_factory(u"%s is one of %s", en_either)
)

translations.define(
    "cocktail.schema.expressions.ExclusionExpression-instance",
    ca = _list_op_translation_factory(u"%s no és %s", ca_either),
    es = _list_op_translation_factory(u"%s no es %s", es_either),
    en = _list_op_translation_factory(u"%s is not %s", en_either)
)

translations.define(
    "cocktail.schema.expressions.ContainsExpression-instance",
    ca = _op_translation_factory(u"%s conté %s"),
    es = _op_translation_factory(u"%s contiene %s"),
    en = _op_translation_factory(u"%s contains %s")
)

translations.define(
    "cocktail.schema.expressions.MatchExpression-instance",
    ca = _op_translation_factory(u"%s passa l'expressió regular %s"),
    es = _op_translation_factory(u"%s pasa la expresión regular %s"),
    en = _op_translation_factory(u"%s matches regular expression %s")
)

translations.define(
    "cocktail.schema.expressions.AnyExpression-instance",
    ca = lambda instance, **kwargs:
        u"té %s" % translations(instance.relation, **kwargs)
        + (
            u" que compleixen (%s)" % u", ".join(
                translations(filter, **kwargs)
                for filter in instance.filters
            )
            if instance.filters else ""
        ),
    es = lambda instance, **kwargs:
        u"tiene %s" % translations(instance.relation, **kwargs)
        + (
            u" que cumplen (%s)" % u", ".join(
                translations(filter, **kwargs)
                for filter in instance.filters
            )
            if instance.filters else ""
        ),
    en = lambda instance, **kwargs:
        u"has %s" % translations(instance.relation, **kwargs)
        + (
            u" matching (%s)" % u", ".join(
                translations(filter, **kwargs)
                for filter in instance.filters
            )
            if instance.filters else ""
        )
)

translations.define(
    "cocktail.schema.expressions.AllExpression-instance",
    ca = lambda instance, **kwargs:
        u"%s compleixen (%s)" % (
            translations(instance.relation, **kwargs),
            u", ".join(
                translations(filter, **kwargs)
                for filter in instance.filters
            )
        ),
    es = lambda instance, **kwargs:
        u"%s cumplen (%s)" % (
            translations(instance.relation, **kwargs),
            u", ".join(
                translations(filter, **kwargs)
                for filter in instance.filters
            )
        ),
    en = lambda instance, **kwargs:
        u"%s match (%s)" % (
            translations(instance.relation, **kwargs),
            u", ".join(
                translations(filter, **kwargs)
                for filter in instance.filters
            )
        )
)

translations.define(
    "cocktail.schema.expressions.AllExpression-instance",
    ca = lambda instance, **kwargs:
        u"%s compleix (%s)" % (
            translations(instance.relation, **kwargs),
            u", ".join(
                translations(filter, **kwargs)
                for filter in instance.filters
            )
        ),
    es = lambda instance, **kwargs:
        u"%s cumple (%s)" % (
            translations(instance.relation, **kwargs),
            u", ".join(
                translations(filter, **kwargs)
                for filter in instance.filters
            )
        ),
    en = lambda instance, **kwargs:
        u"%s matches (%s)" % (
            translations(instance.relation, **kwargs),
            u", ".join(
                translations(filter, **kwargs)
                for filter in instance.filters
            )
        )
)

translations.define(
    "cocktail.schema.expressions.RangeIntersectionExpression-instance",
    ca = _op_translation_factory(
        u"(%s, %s) coincideix amb l'interval (%s, %s)"
    ),
    es = _op_translation_factory(
        u"(%s, %s) coincide con el intervalo (%s, %s)"
    ),
    en = _op_translation_factory(
        u"(%s, %s) intersects with range (%s, %s)"
    )
)

translations.define(
    "cocktail.schema.expressions.IsInstanceExpression-instance",
    ca = _op_translation_factory(u"%s és de tipus %s"),
    es = _op_translation_factory(u"%s es de tipo %s"),
    en = _op_translation_factory(u"%s is instance of %s")
)

translations.define(
    "cocktail.schema.expressions.IsInstanceExpression-instance",
    ca = _op_translation_factory(u"%s no és de tipus %s"),
    es = _op_translation_factory(u"%s no es de tipo %s"),
    en = _op_translation_factory(u"%s is not instance of %s")
)

translations.define(
    "cocktail.schema.expressions.DescendsFromExpression-instance",
    ca = _op_translation_factory(u"%s descendeix de %s"),
    es = _op_translation_factory(u"%s desciende de %s"),
    en = _op_translation_factory(u"%s descends from %s")
)

def _query_translation_factory(filtered_format):

    def translate_query(instance, **kwargs):

        subject = translations(instance.type.name + "-plural", **kwargs)

        if instance.filters:
            return filtered_format % {
                "subject": subject,
                "filters": u", ".join(
                    translations(filter)
                    for filter in instance.filters
                )
            }
        else:
            return subject

    return translate_query

translations.define(
    "cocktail.persistence.query.Query-instance",
    ca = _query_translation_factory(
        "%(subject)s que compleixen: %(filters)s"
    ),
    es = _query_translation_factory(
        "%(subject)s que cumplan: %(filters)s"
    ),
    en = _query_translation_factory(
        "%(subject)s filtered by: %(filters)s"
    )
)

translations.define("cocktail.html.Table remove grouping",
    ca = u"Treure agrupació",
    es = u"Quitar agrupación",
    en = u"Remove grouping"
)

# cocktail.html.Slider
#------------------------------------------------------------------------------
translations.define("cocktail.html.Slider.previous_button",
    ca = u"Anterior",
    es = u"Anterior",
    en = u"Previous"
)

translations.define("cocktail.html.Slider.next_button",
    ca = u"Següent",
    es = u"Siguiente",
    en = u"Next"
)

# cocktail.html.Pager
#------------------------------------------------------------------------------
translations.define("cocktail.html.Pager.first_button",
    ca = u"Primera pàgina",
    es = u"Primera página",
    en = u"First page"
)

translations.define("cocktail.html.Pager.last_button",
    ca = u"Última pàgina",
    es = u"Última página",
    en = u"Last page"
)

translations.define("cocktail.html.Pager.next_button",
    ca = u"Pàgina següent",
    es = u"Página siguiente",
    en = u"Next page"
)

translations.define("cocktail.html.Pager.previous_button",
    ca = u"Pàgina anterior",
    es = u"Página anterior",
    en = u"Previous page"
)

# cocktail.html.AsyncFileUploader
#------------------------------------------------------------------------------
translations.define("cocktail.html.AsyncFileUploader.drop_area",
    ca = u"Arrossega un fitxer aquí per pujar-lo",
    es = u"Arrastra un fichero aquí para subirlo",
    en = u"Drop a file here to upload it",
    pt = u"Upload de arquivo",
    de = u"Upload-Datei"
)

translations.define("cocktail.html.AsyncFileUploader.button",
    ca = u"Pujar fitxer",
    es = u"Subir fichero",
    en = u"Upload file",
    pt = u"Upload de arquivo",
    de = u"Upload-Datei"
)

# cocktail.html.TwitterTimeline
#------------------------------------------------------------------------------
translations.define("cocktail.html.TwitterTimeline.seconds",
    ca = u"fa menys d'un minut",
    es = u"hace menos de un minuto",
    en = u"less than a minute ago"
)

translations.define("cocktail.html.TwitterTimeline.minute",
    ca = u"fa un minut",
    es = u"hace un minuto",
    en = u"about a minute ago"
)

translations.define("cocktail.html.TwitterTimeline.minutes",
    ca = u"fa %(minutes)s minuts",
    es = u"hace %(minutes)s minutos",
    en = u"%(minutes)s minutes ago"
)

translations.define("cocktail.html.TwitterTimeline.hour",
    ca = u"fa una hora",
    es = u"hace una hora",
    en = u"about an hour ago"
)

translations.define("cocktail.html.TwitterTimeline.hours",
    ca = u"fa %(hours)s hores",
    es = u"hace %(hours)s horas",
    en = u"about %(hours)s hours ago"
)

translations.define("cocktail.html.TwitterTimeline.day",
    ca = u"fa un dia",
    es = u"hacen un día",
    en = u"1 day ago"
)

translations.define("cocktail.html.TwitterTimeline.days",
    ca = u"fa %(days)s dies",
    es = u"hace %(days)s días",
    en = u"about %(days)s ago"
)

# cocktail.html.TweetButton
#------------------------------------------------------------------------------
translations.define("cocktail.html.TweetButton",
    ca = u"Tuiteja",
    es = u"Tuitea",
    en = u"Tweet"
)

# html.TranslationDisplay
#------------------------------------------------------------------------------
translations.define(
    "cocktail.html.TranslationDisplay.translation_inheritance_remark",
    ca = lambda source_locale:
        u"Traducció heretada %s"
        % ca_possessive_with_article(
            translations("locale", locale = source_locale)
        ),
    es = lambda source_locale:
        u"Traducción heredada de %s"
        % translations("locale", locale = source_locale),
    en = lambda source_locale:
        u"Translation inherited from %s"
        % translations("locale", locale = source_locale)
)

# IBANEntry
#------------------------------------------------------------------------------
translations.define("cocktail.html.IBANEntry.iban_explanation.summary",
    ca = u"Què és l'IBAN?",
    es = u"¿Qué es el IBAN?",
    en = u"About IBAN codes"
)

translations.define("cocktail.html.IBANEntry.iban_explanation",
    ca = u"""
        <p>
            L'IBAN és un format internacional per indicar comptes bancaris,
            que substitueix els formats nacionals tradicionals. Està suportat
            a múltiples països, i des del febrer de 2014 el seu ús és
            obligatori a tot el territori de la Unió Europea.
        </p>
        <p>
            Normalment, <strong>el codi IBAN apareix a la llibreta o a
            extractes bancaris</strong>. En cas contrari, posi's en contacte amb
            l'entitat bancària.
        </p>
        """,
    es = u"""
        <p>
            IBAN es un formato internacional para números de cuenta bancaria,
            que sustituye los formatos nacionales tradicionales. Está
            soportado en múltiples países, y desde febrero de 2014 su uso es
            obligatorio en todo el territorio de la Unión Europea.
        </p>
        <p>
            Normalmente, <strong>el código IBAN consta en la libreta o
            extractos bancarios</strong>. De no ser así, póngase en contacto
            con la entidad bancaria.
        </p>
        """,
    en = u"""
        <p>
            IBAN is an international format for bank account identifiers that
            replaces the old, national formats. It is used in many countries,
            and from february 2014 its use is mandatory throughout the European
            Union.
        </p>
        <p>
            Tipically <strong>IBAN codes can be fond on bankbooks or bank
            statements</strong>. Otherwise, please contact the bank.
        </p>
        """
)

# SWIFTBICEntry
#------------------------------------------------------------------------------
translations.define("cocktail.html.SWIFTBICEntry.swiftbic_explanation.summary",
    ca = u"Què és el BIC?",
    es = u"¿Qué es el BIC?",
    en = u"About BIC codes"
)

translations.define("cocktail.html.SWIFTBICEntry.swiftbic_explanation",
    ca = u"""
        <p>
            BIC és un format internacional per identificar entitats
            bancàries. A vegades també s'anomena <em>codi SWIFT</em>.
            Normalment, <strong>el codi BIC apareix a la llibreta o a extractes
            bancaris</strong>. En cas contrari, posi's en contacte amb
            l'entitat bancària.
        </p>
        """,
    es = u"""
        <p>
            BIC es un formato internacional para identificar entidades
            bancarias. A veces también se conoce como <em>código SWIFT</em>.
            Normalmente <strong>el código BIC aparece en la libreta o en
            extractos bancarios</strong>. De no ser así, póngase en contacto
            la entidad bancaria.
        </p>
        """,
    en = u"""
        <p>
            BIC is an international format used to specify financial and
            banking entities. The term <em>SWIFT code</em> is sometimes used
            interchangeably. Usually <strong>BIC codes can be found on
            bankbooks or on bank statements</strong>. Otherwise, please contact
            the bank to request it.
        </p>
        """
)

# SearchableCheckList
#------------------------------------------------------------------------------
translations.define(
    "cocktail.html.SearchableCheckList.search_controls.select_all_link",
    ca = u"Seleccionar-ho tot",
    es = u"Seleccionarlo todo",
    en = u"Select all"
)

translations.define(
    "cocktail.html.SearchableCheckList.search_controls.empty_selection_link",
    ca = u"Buidar la selecció",
    es = u"Vaciar la selección",
    en = u"Empty the selection"
)

# SplitSelector
#------------------------------------------------------------------------------
translations.define(
    "cocktail.html.SplitSelector.selected_items_panel.heading",
    ca = u"Seleccionats",
    es = u"Seleccionados",
    en = u"Selected"
)

translations.define(
    "cocktail.html.SplitSelector.selected_items_panel.toggle_button",
    ca = u"Treure",
    es = u"Quitar",
    en = u"Remove"
)

translations.define(
    "cocktail.html.SplitSelector.eligible_items_panel.heading",
    ca = u"No seleccionats",
    es = u"No seleccionados",
    en = u"Not selected"
)

translations.define(
    "cocktail.html.SplitSelector.eligible_items_panel.toggle_button",
    ca = u"Afegir",
    es = u"Añadir",
    en = u"Add"
)

# SuggestionList
#------------------------------------------------------------------------------
translations.define("cocktail.html.SuggestionList.custom_value",
    ca = u"Un altre:",
    es = u"Otro:",
    en = u"Other:"
)

