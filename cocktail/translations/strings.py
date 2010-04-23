#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import re
from datetime import datetime
from decimal import Decimal
from cocktail.pkgutils import get_full_name
from cocktail.translations.translation import translations
from cocktail.translations.helpers import (
    ca_possessive,
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
    en = u"Submit"
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

translations.define("Visible members",
    ca = u"Camps",
    es = u"Campos",
    en = u"Fields"
)

translations.define("Visible languages",
    ca = u"Idiomes",
    es = u"Idiomas",
    en = u"Languages"
)

translations.define("Filters",
    ca = u"Filtres",
    es = u"Filtros",
    en = u"Filters"
)

translations.define("Redirecting",
    ca = u"Redirecció",
    es = u"Redirección",
    en = u"Redirecting"
)

translations.define("Redirection explanation",
    ca = u"S'està redirigint la petició. Si no ets automàticament redirigit, "
         u"prem el botó per continuar navegant pel web.",
    es = u"Se está redirigiendo la petición. Si no eres automáticamente "
         u"redirigido pulsa el botón para proseguir con la navegación.",
    en = u"Redirection in process. If you aren't redirected automatically "
         u"press the button to proceed."
)

translations.define("Redirection button",
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
    en = "%m/%d/%Y"
)

translations.define("jquery_date format",
    ca = "dd/mm/yy",
    es = "dd/mm/yy",
    en = "mm/dd/yy"
)

# -------- ABBREVIATED TRANSLATIONS OF MONTHS
translations.define("month 1 abbr", ca = u"Gen", es = u"Ene", en = u"Jan")
translations.define("month 2 abbr", ca = u"Feb", es = u"Feb", en = u"Feb")
translations.define("month 3 abbr", ca = u"Mar", es = u"Mar", en = u"Mar")
translations.define("month 4 abbr", ca = u"Abr", es = u"Abr", en = u"Apr")
translations.define("month 5 abbr", ca = u"Mai", es = u"May", en = u"May")
translations.define("month 6 abbr", ca = u"Jun", es = u"Jun", en = u"Jun")
translations.define("month 7 abbr", ca = u"Jul", es = u"Jul", en = u"Jul")
translations.define("month 8 abbr", ca = u"Ago", es = u"Ago", en = u"Aug")
translations.define("month 9 abbr", ca = u"Set", es = u"Sep", en = u"Sep")
translations.define("month 10 abbr", ca = u"Oct", es = u"Oct", en = u"Oct")
translations.define("month 11 abbr", ca = u"Nov", es = u"Nov", en = u"Nov")
translations.define("month 12 abbr", ca = u"Des", es = u"Dic", en = u"Dec")

# -------- FULLTEXT TRANSLATIONS OF MONTHS
translations.define("month 1", ca = u"Gener", es = u"Enero", en = u"January")
translations.define("month 2", ca = u"Febrer", es = u"Febrero", en = u"February")
translations.define("month 3", ca = u"Març", es = u"Marzo", en = u"March")
translations.define("month 4", ca = u"Abril", es = u"Abril", en = u"April")
translations.define("month 5", ca = u"Maig", es = u"Mayo", en = u"May")
translations.define("month 6", ca = u"Juny", es = u"Junio", en = u"June")
translations.define("month 7", ca = u"Juliol", es = u"Julio", en = u"July")
translations.define("month 8", ca = u"Agost", es = u"Agosto", en = u"August")
translations.define("month 9", ca = u"Setembre", es = u"Septiembre", en = u"September")
translations.define("month 10", ca = u"Octubre", es = u"Octubre", en = u"October")
translations.define("month 11", ca = u"Novembre", es = u"Noviembre", en = u"November")
translations.define("month 12", ca = u"Desembre", es = u"Diciembre", en = u"December")

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

DATE_STYLE_NUMBERS = 1
DATE_STYLE_ABBR = 2
DATE_STYLE_TEXT = 3

def _date_instance_ca(instance, style = DATE_STYLE_NUMBERS):
    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("date format"))
    elif style == DATE_STYLE_ABBR:
        return u"%s %s %s" % (
            instance.day,
            translations(u"month %s abbr" % instance.month),
            instance.year
        )
    elif style == DATE_STYLE_TEXT:
        return u"%s %s de %s" % (
            instance.day,
            ca_possessive(
                translations(u"month %s" % instance.month).lower()
            ),
            instance.year
        )

def _date_instance_es(instance, style = DATE_STYLE_NUMBERS):
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

def _date_instance_en(instance, style = DATE_STYLE_NUMBERS):
    if style == DATE_STYLE_NUMBERS:
        return instance.strftime(translations("date format"))
    elif style == DATE_STYLE_ABBR:
        return u"%s %s %s" % (
            instance.year,
            translations(u"month %s abbr" % instance.month),
            instance.day
        )
    elif style == DATE_STYLE_TEXT:
        return u"%s %s %s" % (
            instance.year,
            translations(u"month %s" % instance.month),
            instance.day
        )

translations.define("date-instance",
    ca = _date_instance_ca,
    es = _date_instance_es,
    en = _date_instance_en
)

translations.define("datetime-instance",
    ca = lambda instance, style = DATE_STYLE_NUMBERS:
        _date_instance_ca(instance, style) + instance.strftime(" %H:%M:%S"),
    es = lambda instance, style = DATE_STYLE_NUMBERS:
        _date_instance_es(instance, style) + instance.strftime(" %H:%M:%S"),
    en = lambda instance, style = DATE_STYLE_NUMBERS:
        _date_instance_en(instance, style) + instance.strftime(" %H:%M:%S")
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

translations.define("date range",
    ca = _date_range_ca,
    es = _date_range_es,
    en = _date_range_en
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

translations.define("translated into",
    ca = lambda lang: "en " + translations(lang),
    es = lambda lang: "en " + translations(lang),
    en = lambda lang: "in " + translations(lang)
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
    
    from cocktail.schema import RelationMember

    desc = [
        translations(member).lower()
        for member, validable in error.path
        if isinstance(member, RelationMember)
    ]
    
    if error.language:
        desc.append("%s (%s)" % (
            translations(error.member).lower(),
            translations(error.language)
        ))
    else:
        desc.append(translations(error.member).lower())

    return u" &gt; ".join(desc)

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
        % member_identifier(instance)
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
        % member_identifier(instance)
)

translations.define("cocktail.schema.exceptions.MinValueError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de ser igual o superior a %s"
        % (member_identifier(instance), instance.min),
    es = lambda instance:
        u"El campo <em>%s</em> debe ser igual o superior a %s"
        % (member_identifier(instance), instance.min),
    en = lambda instance:
        u"The <em>%s</em> field must be greater or equal than %s"
        % (member_identifier(instance), instance.min)
)

translations.define("cocktail.schema.exceptions.MaxValueError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de ser igual o inferior a %s"
        % (member_identifier(instance), instance.max),
    es = lambda instance:
        u"El campo <em>%s</em> debe ser igual o inferior a %s"
        % (member_identifier(instance), instance.max),
    en = lambda instance:
        u"The <em>%s</em> field must be lower or equal than %s"
        % (member_identifier(instance), instance.max)
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
    en = lambda: _thousands_parser(",", ".")
)

translations.define("decimal.Decimal-instance",
    ca = lambda instance: _serialize_thousands(instance, ".", ","),
    es = lambda instance: _serialize_thousands(instance, ".", ","),
    en = lambda instance: _serialize_thousands(instance, ",", ".")
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
            print format
            print operands

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
    "cocktail.schema.expressions.StartsWithExpression-instance",
    ca = _op_translation_factory(u"%s conté la cerca %s"),
    es = _op_translation_factory(u"%s contiene la búsqueda %s"),
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
                    translations(filter, **kwargs)
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

