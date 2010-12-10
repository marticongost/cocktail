#-*- coding: utf-8 -*-
u"""Defines the `DocumentMetadata` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from time import time
from threading import local
from cocktail.modeling import getter, OrderedSet
from cocktail.cache import Cache
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

        A `cache <cocktail.cache.Cache>` of rendered content.
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
        self.write = self.__content.append
        self.rendered_client_model = rendered_client_model

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
            cache_key = None

            if self.cache is not None and self.cache.enabled:

                element.bind()

                if element.cached and element.rendered:
                    cache_key = (self.get_cache_key(), element.get_cache_key())
                    cached_rendering = self.cache.get_value(
                        cache_key,
                        default = None,
                        invalidation = element.get_cache_invalidation
                    )

                    # Cached rendering
                    if cached_rendering is not None:
                        self.update(cached_rendering)
                        return

            element.ready()

            # Skip invisible elements
            if element.rendered:
            
                # Delay rendering of client models, unless they are being 
                # rendered explicitly
                if element.client_model \
                and element is not self.rendered_client_model:
                    if self.collect_metadata:
                        self.document_metadata \
                            .client_models[element.client_model] = element
                    return

                # Set up a separate rendering context for cached elements, and
                # add it to the cache
                if cache_key and element.cached:
                    target_rendering = self.__class__(                    
                        renderer = self.renderer,
                        collect_metadata = self.collect_metadata,
                        cache = self.cache,
                        rendered_client_model = self.rendered_client_model
                    )
                    self.cache.set_value(
                        cache_key,
                        target_rendering,
                        element.cache_expiration
                    )
                else:
                    target_rendering = self

                # Render the element and collect metadata
                element._render(target_rendering)

                if target_rendering.collect_metadata:
                    target_rendering.document_metadata.collect(
                        element,
                        self.rendered_client_model is not None
                    )

                # After rendering to the cache, render to the main stream as well
                if target_rendering is not self:
                    self.update(target_rendering)

        finally:
            if setup_id:
                del _thread_data.prefix
                del _thread_data.generated_id
            
            _thread_data.rendering = prev_rendering

    def get_cache_key(self):
        return self.renderer.__class__

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
        return u"".join(self.__content)


class IdGenerationError(Exception):
    """An exception raised when trying to
    `generate a unique identifier <generate_id>` outside of a rendering
    operation.
    """
    def __str__(self):
        return "Element identifiers can only be generated while rendering"

