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
    ca = lambda t, k, page_range, item_count: \
        u"Mostrant resultats <strong>%d-%d</strong> de %d" % (
            page_range[0], page_range[1], item_count
        ),
    es = lambda t, k, page_range, item_count: \
        u"Mostrando resultados <strong>%d-%d</strong> de %d" % (
            page_range[0], page_range[1], item_count
        ),
    en = lambda t, k, page_range, item_count: \
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

