#-*- coding: utf-8 -*-
u"""Defines the `DocumentMetadata` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import OrderedSet


class DocumentMetadata(object):
    """An object that aggregates all the supplemental assets and metadata
    required for rendering a set of HTML elements.

    .. attribute:: page_title

        The content that should be placed in the document's <title> element.

    .. attribute:: language

        The language for the outtermost element.

    .. attribute:: content_type

        The content type of the produced document.

    .. attribute:: charset

        The charset of the produced document.

    .. attribute:: meta

        A dicionary containing all the meta tags required by rendered elements.

    .. attribute:: resources

        An ordered set containing all the scripts and stylesheets required by
        rendered elements. Resources are arranged in the same order that they
        should be included.

    .. attribute:: document_ready_callbacks

        A list of functions that should be called after the document has been
        created and filled with the metadata.

    .. attribute:: client_params

        Values that should be declared as custom attributes of specific DOM
        nodes, using JSON serialization. A dictionary mapping DOM node IDs to
        dictionaries of key/value pairs.
    
    .. attribute:: client_variables

        Values that should be declared as client side variables, using JSON
        serialization.

    .. attribute:: client_translations

        A set of translation keys that should be made available to client side
        code.

    .. attribute:: client_code

        A list of arbitrary snippets of client side code.

    .. attribute:: client_models

        A dictionary of elements that should be made available to client side
        code as factory functions.
    """

    def __init__(self):
        self.doctype = None
        self.page_title = None
        self.language = None
        self.content_type = "text/html"
        self.charset = "utf-8"
        self.meta = {}
        self.resources = OrderedSet()
        self.document_ready_callbacks = []
        self.client_params = {}
        self.client_variables = {}
        self.client_translations = set()
        self.client_code = {}
        self.client_models = {}

    def embedding_markup(self, renderer = None):

        from cocktail.html.document import HTMLDocument

        document = HTMLDocument()
        document.metadata = self
        document.ready()
        document.title.visible = False
        document.meta_tags.visible = False

        return document.head.render(
            renderer = renderer,
            collect_metadata = False,
            cache = None
        )

    def collect(self, element):

        if element.page_doctype:
            self.doctype = element.page_doctype

        if element.page_title:
            self.page_title = element.page_title

        if element.language:
            self.language = element.language

        if element.page_content_type:
            self.content_type = element.page_content_type

        if element.page_charset:
            self.charset = element.page_charset

        self.meta.update(element.meta)
        self.resources.extend(element.resources)
        self.document_ready_callbacks.extend(element.document_ready_callbacks)
        self.client_translations.update(element.client_translations)
        self.client_variables.update(element.client_variables)

        id = element["id"]

        # Client code
        if element.client_code:
            old_code = self.client_code.get(id)
            if old_code is None:
                self.client_code[id] = list(element.client_code)
            else:
                old_code.extend(element.client_code)

        # Client parameters
        if element.client_params:
            old_values = self.client_params.get(id)
            if old_values is None:
                self.client_params[id] = element.client_params.copy()
            else:
                old_values.update(element.client_params)

    def update(self, metadata):

        if metadata.page_title:
            self.page_title = metadata.page_title

        if metadata.language:
            self.language = metadata.language

        if metadata.content_type:
            self.content_type = metadata.content_type

        if metadata.charset:
            self.charset = metadata.charset

        self.meta.update(metadata.meta)
        self.resources.extend(metadata.resources)
        self.document_ready_callbacks.extend(metadata.document_ready_callbacks)
        self.client_variables.update(metadata.client_variables)
        self.client_translations.update(metadata.client_translations)
        self.client_models.update(metadata.client_models)
            
        # Client code
        for id, new_code in metadata.client_code.iteritems():
            old_code = self.client_code.get(id)
            if old_code is None:
                self.client_code[id] = list(new_code)
            else:
                old_code.update(new_code)

        # Client parameters
        for id, new_values in metadata.client_params.iteritems():
            old_values = self.client_params.get(id)
            if old_values is None:
                self.client_params[id] = new_values.copy()
            else:
                old_values.update(new_values)

