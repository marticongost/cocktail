#-*- coding: utf-8 -*-
u"""
Provides classes for building reusable (X)HTML components.

This package supplies all the necessary building blocks to create visual
components that can be easily composited, inherited and overlayed to maximize
code reuse in the presentation layer.

Some of its most notable features include:

* Components can be written in plain python or in XML
* Handles dependencies on client side scripts and stylesheets
* Integration with jQuery
* Support for multiple rendering modes (HTML4, XHTML)

Also, an extensive set of ready made components is provided as well, covering a
wide assortment of needs: forms, tables, calendars, etc.
"""
from cocktail.html.renderers import (
    Renderer,
    html4_renderer,
    html5_renderer,
    xhtml_renderer,
    xhtml5_renderer
)
from cocktail.html.rendering import Rendering
from cocktail.html.element import (
    Element,
    Content,
    TranslatedValue,
    PlaceHolder
)
from cocktail.html.resources import (
    Resource, 
    Script,
    StyleSheet
)
from cocktail.html.documentmetadata import DocumentMetadata
from cocktail.html.overlay import Overlay
from cocktail.html.utils import (
    alternate_classes,
    first_last_classes,
    html5_tag,
    html5_attr,
    escape_attrib
)

