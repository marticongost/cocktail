#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase
from nose.tools import assert_raises

class CacheTestCase(TestCase):

    def setUp(self):
        from cocktail.html.rendering import rendering_cache
        rendering_cache.clear()

    def test_elements_reuse_cached_content(self):
        from cocktail.html.element import Element

        e = Element("div")
        e.append("Hello, world")
        e.cached = True
        e.get_cache_key = lambda: "test"

        e.render()
        e.append("!!!")
        
        assert e.render() == "<div>Hello, world</div>"

        e.cached = False
        assert e.render() == "<div>Hello, world!!!</div>"

    def test_cached_content_is_indexed_by_cache_key(self):
        from cocktail.html.element import Element

        a = Element("div")
        a.append("a")
        a.cached = True
        a.get_cache_key = lambda: "a"
        a.render()

        b = Element("div")
        b.append("b")
        b.cached = True
        b.get_cache_key = lambda: "b"
        b.render()

        x = Element("div")
        x.append("x")
        x.cached = True
        x.get_cache_key = lambda: "x"
        x.render()

        assert x.render() == "<div>x</div>"
        
        x.get_cache_key = lambda: "a"
        assert x.render() == "<div>a</div>"

        x.get_cache_key = lambda: "b"
        assert x.render() == "<div>b</div>"

    def test_cached_content_must_define_a_cache_key(self):
        from cocktail.html.element import Element

        e = Element("div")
        e.append("Hello, world")
        e.cached = True
        
        assert_raises(KeyError, e.render)

    def test_cached_content_respects_renderer_class(self):
        from cocktail.html.element import Element
        from cocktail.html.renderers import html4_renderer, xhtml_renderer

        img = Element("img")
        img.cached = True
        img.get_cache_key = lambda: "test"        
        img.render()

        html = img.render(renderer = html4_renderer)
        assert html == "<img>"

        xhtml = img.render(renderer = xhtml_renderer) 
        assert xhtml == "<img/>"

    def test_cached_content_includes_resources(self):
        
        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.get_cache_key = lambda: "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.add_resource("foo.js")
            e.append(child)

        e.render()

        assert "foo.js" in e.render_page()

    def test_cached_content_includes_client_parameters(self):
        
        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.get_cache_key = lambda: "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.set_client_param("foo", "bar")
            e.append(child)

        e.render()

        assert "foo" in e.render_page()

    def test_cached_content_includes_client_variables(self):
        
        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.get_cache_key = lambda: "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.set_client_variable("foo", "bar")
            e.append(child)

        e.render()

        assert "foo" in e.render_page()

    def test_cached_content_includes_head_elements(self):
        
        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.get_cache_key = lambda: "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.add_head_element(Element("foo"))
            e.append(child)

        e.render()

        assert "foo" in e.render_page()

    def test_cached_content_includes_meta_tags(self):
        
        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.get_cache_key = lambda: "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.set_meta("foo", "bar")
            e.append(child)

        e.render()

        assert "foo" in e.render_page()

    def test_cached_content_includes_client_translations(self):
        
        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.get_cache_key = lambda: "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.add_client_translation("foo")
            e.append(child)

        e.render()

        assert "foo" in e.render_page()

    def test_elements_can_define_cache_expiration(self):

        from time import sleep
        from cocktail.html.element import Element
        
        e = Element()
        e.cached = True
        e.get_cache_key = lambda: "test"
        e.cache_expiration = 1
        e.render()

        e.append("foo")
        assert "foo" not in e.render()

        sleep(1)
        assert "foo" in e.render()

    def test_elements_can_invalidate_cached_content(self):

        from time import time, sleep
        from datetime import datetime
        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.get_cache_key = lambda: "test_with_timestamps"
        
        # Older timestamp: cached content should still be valid
        t1 = time()
        e.render()
        e.append("foo")
        e.get_cache_invalidation = lambda: t1
        assert "foo" not in e.render()

        # Newer timestamp: cached content should be invalidated 
        t2 = time()
        e.get_cache_invalidation = lambda: t2
        assert "foo" in e.render()

        e = Element()
        e.cached = True
        e.get_cache_key = lambda: "test_with_datetime"
        
        # Older datetime: cached content should still be valid
        t1 = datetime.now()
        e.render()
        e.append("foo")
        e.get_cache_invalidation = lambda: t1
        assert "foo" not in e.render()

        # Newer timestamp: cached content should be invalidated 
        sleep(1)
        t2 = datetime.now()
        e.get_cache_invalidation = lambda: t2
        assert "foo" in e.render()

