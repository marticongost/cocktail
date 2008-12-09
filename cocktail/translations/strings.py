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

translations.define(True,
    ca = u"Sí",
    es = u"Sí",
    en = u"Yes"
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

translations.define("CollectionView selection",
    ca = u"Seleccionar:",
    es = u"Seleccionar:",
    en = u"Select:"
)

translations.define("CollectionView all",
    ca = u"Tots",
    es = u"Todos",
    en = u"All"
)

translations.define("CollectionView none",
    ca = u"Cap",
    es = u"Ninguno",
    en = u"None"
)

translations.define("Translations",
    ca = u"Traduccions",
    es = u"Traducciones",
    en = u"Translations"
)

translations.define("datetime-instance",
    ca = lambda instance: instance.strftime("%d/%m/%Y %H:%M:%S"),
    es = lambda instance: instance.strftime("%d/%m/%Y %H:%M:%S"),
    en = lambda instance: instance.strftime("%Y-%m-%d %H:%M:%S")
)

# html.FilterBox
#------------------------------------------------------------------------------
translations.define("cocktail.html.FilterBox add filter",
    ca = u"Afegir filtre",
    es = u"Añadir filtro",
    en = u"Add filter"
)

translations.define("cocktail.html.FilterBox clear filters",
    ca = u"Netejar filtres",
    es = u"Limpiar filtros",
    en = u"Clear filters"
)

translations.define("cocktail.html.FilterBox apply filters",
    ca = u"Aplicar",
    es = u"Aplicar",
    en = u"Apply"
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

translations.define("UserFilter.language",
    ca = u"en",
    es = u"en",
    en = u"in"
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

translations.define("translated into",
    ca = lambda lang: "en " + translate(lang, "ca"),
    es = lambda lang: "en " + translate(lang, "es"),
    en = lambda lang: "in " + translate(lang, "en")
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
def member_identifier(error, language):
    if error.language:
        return "%s (%s)" % (
            translate(error.member, language).lower(),
            translate(error.language, language)
        )
    else:
        return translate(error.member, language).lower()

translations.define("cocktail.schema.exceptions.ValueRequiredError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> no pot estar buit"
        % member_identifier(instance, "ca"),
    es = lambda instance:
        u"El campo <em>%s</em> no puede estar vacío"
        % member_identifier(instance, "es"),
    en = lambda instance:
        u"The <em>%s</em> field can't be empty"
        % member_identifier(instance, "en")
)

translations.define("cocktail.schema.exceptions.NoneRequiredError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha d'estar buit"
        % member_identifier(instance, "ca"),
    es = lambda instance:
        u"El campo <em>%s</em> debe estar vacío"
        % member_identifier(instance, "es"),
    en = lambda instance:
        u"The <em>%s</em> field must be empty"
        % member_identifier(instance, "en")
)

translations.define("cocktail.schema.exceptions.TypeCheckError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> té un tipus incorrecte"
        % member_identifier(instance, "ca"),
    es = lambda instance:
        u"El campo <em>%s</em> tiene un tipo incorrecto"
        % member_identifier(instance, "es"),
    en = lambda instance:
        u"The <em>%s</em> field is of the wrong type"
        % member_identifier(instance, "en")
)

translations.define("cocktail.schema.exceptions.EnumerationError-instance",
    ca = lambda instance:
        u"El valor del camp <em>%s</em> no és un dels permesos"
        % member_identifier(instance, "ca"),
    es = lambda instance:
        u"El campo <em>%s</em> no es uno de los permitidos"
        % member_identifier(instance, "es"),
    en = lambda instance:
        u"Wrong choice on field <em>%s</em>"
        % member_identifier(instance, "en")
)

translations.define("cocktail.schema.exceptions.MinLengthError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de tenir un mínim de %d caràcters"
        % (member_identifier(instance, "ca"), instance.min),
    es = lambda instance:
        u"El campo <em>%s</em> debe tener un mínimo de %d caracteres"
        % (member_identifier(instance, "es"), instance.min),
    en = lambda instance:
        u"The <em>%s</em> field must be at least %d characters long"
        % (member_identifier(instance, "en"), instance.min)
)

translations.define("cocktail.schema.exceptions.MaxLengthError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de tenir un màxim de %d caràcters"
        % (member_identifier(instance, "ca"), instance.max),
    es = lambda instance:
        u"El campo <em>%s</em> debe tener un máximo de %d caracteres"
        % (member_identifier(instance, "es"), instance.max),
    en = lambda instance:
        u"The <em>%s</em> field can't be more than %d characters long"
        % (member_identifier(instance, "en"), instance.max)
)

translations.define("cocktail.schema.exceptions.FormatError-instance",
    ca = lambda instance:
        u"El format del camp <em>%s</em> és incorrecte"
        % member_identifier(instance, "ca"),
    es = lambda instance:
        u"El formato del campo <em>%s</em> es incorrecto"
        % member_identifier(instance, "es"),
    en = lambda instance:
        u"The <em>%s</em> field has a wrong format"
        % member_identifier(instance, "en")
)

translations.define("cocktail.schema.exceptions.MinValueError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de ser igual o superior a %s"
        % (member_identifier(instance, "ca"), instance.min),
    es = lambda instance:
        u"El campo <em>%s</em> debe ser igual o superior a %s"
        % (member_identifier(instance, "es"), instance.min),
    en = lambda instance:
        u"The <em>%s</em> field must be greater or equal than %s"
        % (member_identifier(instance, "en"), instance.min)
)

translations.define("cocktail.schema.exceptions.MaxValueError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de ser igual o inferior a %s"
        % (member_identifier(instance, "ca"), instance.max),
    es = lambda instance:
        u"El campo <em>%s</em> debe ser igual o inferior a %s"
        % (member_identifier(instance, "es"), instance.max),
    en = lambda instance:
        u"The <em>%s</em> field must be lower or equal than %s"
        % (member_identifier(instance, "en"), instance.max)
)

translations.define("cocktail.schema.exceptions.MinItemsError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> ha de contenir %d o més elements"
        % (member_identifier(instance, "ca"), instance.min),
    es = lambda instance:
        u"El campo <em>%s</em> debe contener %d o más elementos"
        % (member_identifier(instance, "es"), instance.min),
    en = lambda instance:
        u"The <em>%s</em> field must contain %d or more items"
        % (member_identifier(instance, "en"), instance.min)
)

translations.define("cocktail.schema.exceptions.MaxItemsError-instance",
    ca = lambda instance:
        u"El camp <em>%s</em> no pot contenir més de %d elements"
        % (member_identifier(instance, "ca"), instance.max),
    es = lambda instance:
        u"El campo <em>%s</em> no puede contener más de %d elementos"
        % (member_identifier(instance, "es"), instance.max),
    en = lambda instance:
        u"The <em>%s</em> field can't contain more than %d items"
        % (member_identifier(instance, "en"), instance.max)
)

translations.define(
    "cocktail.persistence.persistentobject.UniqueValueError-instance",
    ca = lambda instance:
        u"El valor indicat pel camp <em>%s</em> ja existeix a la base de dades"
        % member_identifier(instance, "ca"),
    es = lambda instance:
        u"El valor indicado para el campo <em>%s</em> ya existe en la base de "
        u"datos"
        % member_identifier(instance, "es"),
    en = lambda instance:
        u"The value of the <em>%s</em> field is already in use"
        % member_identifier(instance, "en")
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

