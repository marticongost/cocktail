#-*- coding: utf-8 -*-
u"""Defines the `DocumentMetadata` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from time import time
from threading import local
from cocktail.translations import get_language
from cocktail.modeling import getter, OrderedSet
from cocktail.caching import Cache, CacheKeyError
from cocktail.html.documentmetadata import DocumentMetadata

rendering_cache = Cache()

_thread_data = local()

def get_current_rendering():
    """Gets the `Renderer` object used by the current thread."""
    return getattr(_thread_data, "rendering", None)

generated_id_format = "cocktail-element-%s-%d"

def generate_id():
    try:
        incremental_id = _thread_data.generated_id
    except AttributeError:
        raise IdGenerationError()

    _thread_data.generated_id += 1

    return generated_id_format % (
        _thread_data.prefix,
        incremental_id
    )


class Rendering(object):
    """A rendering operation, used to incrementally produce the markup for one
    or more elements.

    .. attribute:: renderer

        The `renderer <Renderer>` used to format HTML elements.

    .. attribute:: collect_metadata

        Determines if resources and meta data (scripts, stylesheets, meta tags,
        etc) defined by rendered elements should be evaluated and collected..

    .. attribute:: document_metadata

        A `DocumentMetadata` instance listing the resources and meta data
        collected from rendered elements.

        Will be empty if `collect_metadata` is set to False.

    .. attribute:: cache

        A `cache <cocktail.caching.Cache>` of rendered content.
    """

    def __init__(self,
        renderer,
        collect_metadata = True,
        document_metadata = None,
        cache = rendering_cache,
        rendered_client_model = None):

        self.renderer = renderer
        self.collect_metadata = collect_metadata
        self.document_metadata = document_metadata or DocumentMetadata()
        self.cache = cache
        self.__content = []
        self.rendered_client_model = rendered_client_model

    def write(self, chunk):
        self.__content.append(chunk)

    def render_element(self, element):

        # Register the current rendering
        prev_rendering = getattr(_thread_data, "rendering", None)
        _thread_data.rendering = self

        # Setup incremental id generation
        setup_id = not hasattr(_thread_data, "generated_id")
        if setup_id:
            _thread_data.prefix = str(time()).replace(".", "")
            _thread_data.generated_id = 0

        try:
            # Bring the element to the 'binding' stage
            element.bind()

            # Skip hidden elements
            if not element.visible:
                return

            # Determine if the element needs to be rendered apart, to be
            # included as a client model
            rendered_as_client_model = (
                element.client_model
                and element.client_model != self.rendered_client_model
            )
            if rendered_as_client_model:
                rendering = self.__class__(
                    renderer = self.renderer,
                    cache = self.cache,
                    rendered_client_model = element
                )
            else:
                rendering = self

            # Possibly render the element from the cache
            rendered_from_cache = False

            if rendering.cache is not None and element.cached:
                cache_key = (rendering.get_cache_key(), element.cache_key)
            else:
                cache_key = None

            if cache_key:
                try:
                    cached_value, cached_expiration, cached_tags = \
                        rendering.cache.retrieve_with_metadata(cache_key)
                except CacheKeyError:
                    pass
                else:
                    cached_content, cached_metadata = cached_value
                    rendering.__content.extend(cached_content)
                    rendering.document_metadata.update(cached_metadata)
                    rendered_from_cache = True

                    if cached_tags:
                        element.cache_tags.update(cached_tags)

                    element.update_cache_expiration(cached_expiration)

            # Otherwise, render the element from scratch
            if not rendered_from_cache:

                # Bring the element to the 'ready' stage
                element.ready()

                # Skip hidden elements
                if not element.rendered:
                    return

                # Cached elements are rendered using a separate rendering
                # buffer, which is stored in the rendering cache first and then
                # replicated to the main rendering buffer.
                if cache_key:
                    cache_rendering = rendering.__class__(
                        renderer = rendering.renderer,
                        collect_metadata = rendering.collect_metadata,
                        cache = rendering.cache,
                        rendered_client_model = rendering.rendered_client_model
                    )

                    element._render(cache_rendering)

                    if cache_rendering.collect_metadata:
                        cache_rendering.document_metadata.collect(
                            element,
                            self.rendered_client_model is not None
                        )

                    tags = element.cache_tags
                    language = get_language()
                    if language:
                        tags.add("lang-" + language)

                    rendering.cache.store(
                        cache_key,
                        (
                            cache_rendering.__content,
                            cache_rendering.document_metadata
                        ),
                        expiration = element.cache_expiration,
                        tags = tags
                    )
                    rendering.update(cache_rendering)

                # Non cached elements are rendered directly onto the main
                # rendering buffer.
                else:
                    element._render(rendering)

                    if rendering.collect_metadata:
                        rendering.document_metadata.collect(
                            element,
                            self.rendered_client_model is not None
                        )

            # Store the markup and metadata for client models, they will be
            # included in the document by the HTMLDocument class
            if rendered_as_client_model and self.collect_metadata:
                self.document_metadata.client_models[element.client_model] = (
                    rendering.markup(),
                    rendering.document_metadata
                )

        finally:
            if setup_id:
                del _thread_data.prefix
                del _thread_data.generated_id

            _thread_data.rendering = prev_rendering

    def get_cache_key(self):
        return self.renderer.__class__.__name__

    def update(self, rendering):
        """Extend the rendering state with data from another rendering.

        The main use case for this method is reusing content and metadata from
        the rendering cache.

        :param rendering: The object to read data from.
        :type rendering: `Rendering`
        """
        self.__content.extend(rendering.__content)
        self.document_metadata.update(rendering.document_metadata)

    def markup(self):
        """Returns the accumulated markup text from write operations."""
        try:
            return u"".join(self.__content)
        except TypeError:
            for i, chunk in enumerate(self.__content):
                if chunk is None:
                    raise TypeError(
                        "Rendering chunk #%d contains a None value (%s)"
                        % (i, self.__content[max(0, i - 10):i + 1])
                    )
            else:
                raise


class IdGenerationError(Exception):
    """An exception raised when trying to
    `generate a unique identifier <generate_id>` outside of a rendering
    operation.
    """
    def __str__(self):
        return "Element identifiers can only be generated while rendering"

