#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.translations.translation import translations, translate

translations.define(True,
    ca = u"Sí",
    es = u"Sí",
    en = u"Yes"
)

translations.define(False,
    ca = u"No",
    es = u"No",
    en = u"No"
)

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

translations.define("Submit",
    ca = u"Confirmar",
    es = u"Confirmar",
    en = u"Submit"
)

translations.define("Item count",
    ca = lambda page_range, item_count: \
        u"Mostrant resultats <strong>%d-%d</strong> de %d" % (
            page_range[0], page_range[1], item_count
        ),
    es = lambda page_range, item_count: \
        u"Mostrando resultados <strong>%d-%d</strong> de %d" % (
            page_range[0], page_range[1], item_count
        ),
    en = lambda page_range, item_count: \
        u"Showing results <strong>%d-%d</strong> of %d" % (
            page_range[0], page_range[1], item_count
        )
)

translations.define("Results per page",
    ca = u"Resultats per pàgina",
    es = u"Resultados por página",
    en = u"Results per page"
)

translations.define("No results",
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

# Validation errors
#------------------------------------------------------------------------------
translations.define("cocktail.schema.exceptions.ValueRequiredError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> no pot estar buit"
        % translate(instance.member, "ca"),
    es = lambda instance:
        u"El campo <em>%s</em> no puede estar vacío"
        % translate(instance.member, "es"),
    en = lambda instance:
        u"The <em>%s</em> field can't be empty"
        % translate(instance.member, "en")
)

translations.define("cocktail.schema.exceptions.NoneRequiredError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha d'estar buit"
        % translate(instance.member, "ca"),
    es = lambda instance:
        u"El campo <em>%s</em> debe estar vacío"
        % translate(instance.member, "es"),
    en = lambda instance:
        u"The <em>%s</em> field must be empty"
        % translate(instance.member, "en")
)

translations.define("cocktail.schema.exceptions.TypeCheckError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> té un tipus incorrecte"
        % translate(instance.member, "ca"),
    es = lambda instance:
        u"El campo <em>%s</em> tiene un tipo incorrecto"
        % translate(instance.member, "es"),
    en = lambda instance:
        u"The <em>%s</em> field is of the wrong type"
        % translate(instance.member, "en")
)

translations.define("cocktail.schema.exceptions.EnumerationError-instance",
    ca = lambda instance:
        u"El valor del camp <em>%s</em> no és un dels permesos"
        % translate(instance.member, "ca"),
    es = lambda instance:
        u"El campo <em>%s</em> no es uno de los permitidos"
        % translate(instance.member, "es"),
    en = lambda instance:
        u"Wrong choice on field <em>%s</em>"
        % translate(instance.member, "en")
)

translations.define("cocktail.schema.exceptions.MinLengthError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de tenir un mínim de %d caràcters"
        % (translate(instance.member, "ca"), instance.min),
    es = lambda instance:
        u"El campo <em>%s</em> debe tener un mínimo de %d caracteres"
        % (translate(instance.member, "es"), instance.min),
    en = lambda instance:
        u"The <em>%s</em> field must be at least %d characters long"
        % (translate(instance.member, "en"), instance.min)
)

translations.define("cocktail.schema.exceptions.MaxLengthError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de tenir un màxim de %d caràcters"
        % (translate(instance.member, "ca"), instance.max),
    es = lambda instance:
        u"El campo <em>%s</em> debe tener un máximo de %d caracteres"
        % (translate(instance.member, "es"), instance.max),
    en = lambda instance:
        u"The <em>%s</em> field can't be more than %d characters long"
        % (translate(instance.member, "en"), instance.max)
)

translations.define("cocktail.schema.exceptions.FormatError-instance",
    ca = lambda instance:
        u"El format del camp <em>%s</em> és incorrecte"
        % translate(instance.member, "ca"),
    es = lambda instance:
        u"El formato del campo <em>%s</em> es incorrecto"
        % translate(instance.member, "es"),
    en = lambda instance:
        u"The <em>%s</em> field has a wrong format"
        % translate(instance.member, "en")
)

translations.define("cocktail.schema.exceptions.MinValueError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de ser igual o superior a %s"
        % (translate(instance.member, "ca"), instance.min),
    es = lambda instance:
        u"El campo <em>%s</em> debe ser igual o superior a %s"
        % (translate(instance.member, "es"), instance.min),
    en = lambda instance:
        u"The <em>%s</em> field must be greater or equal than %s"
        % (translate(instance.member, "en"), instance.min)
)

translations.define("cocktail.schema.exceptions.MaxValueError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de ser igual o inferior a %s"
        % (translate(instance.member, "ca"), instance.max),
    es = lambda instance:
        u"El campo <em>%s</em> debe ser igual o inferior a %s"
        % (translate(instance.member, "es"), instance.max),
    en = lambda instance:
        u"The <em>%s</em> field must be lower or equal than %s"
        % (translate(instance.member, "en"), instance.max)
)

translations.define("cocktail.schema.exceptions.MinItemsError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de contenir %d o més elements"
        % (translate(instance.member, "ca"), instance.min),
    es = lambda instance:
        u"El campo <em>%s</em> debe contener %d o más elementos"
        % (translate(instance.member, "es"), instance.min),
    en = lambda instance:
        u"The <em>%s</em> field must contain %d or more items"
        % (translate(instance.member, "en"), instance.min)
)

translations.define("cocktail.schema.exceptions.MaxItemsError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> no pot contenir més de %d elements"
        % (translate(instance.member, "ca"), instance.max),
    es = lambda instance:
        u"El campo <em>%s</em> no puede contener más de %d elementos"
        % (translate(instance.member, "es"), instance.max),
    en = lambda instance:
        u"The <em>%s</em> field can't contain more than %d items"
        % (translate(instance.member, "en"), instance.max)
)

