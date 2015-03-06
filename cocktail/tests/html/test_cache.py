#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase
from nose.tools import assert_raises

class CacheTestCase(TestCase):

    def setUp(self):
        from cocktail.caching import Cache, MemoryCacheStorage
        from cocktail.html.rendering import rendering_cache
        self.cache = Cache()
        self.cache.storage = MemoryCacheStorage()

    def test_elements_reuse_cached_content(self):
        from cocktail.html.element import Element

        e = Element("div")
        e.append("Hello, world")
        e.cached = True
        e.cache_key = "test"

        e.render(cache = self.cache)
        e.append("!!!")

        assert e.render(cache = self.cache) == "<div>Hello, world</div>"

        e.cached = False
        assert e.render(cache = self.cache) == "<div>Hello, world!!!</div>"

    def test_cached_content_is_indexed_by_cache_key(self):
        from cocktail.html.element import Element

        a = Element("div")
        a.append("a")
        a.cached = True
        a.cache_key = "a"
        a.render(cache = self.cache)

        b = Element("div")
        b.append("b")
        b.cached = True
        b.cache_key ="b"
        b.render(cache = self.cache)

        x = Element("div")
        x.append("x")
        x.cached = True
        x.cache_key = "x"
        x.render(cache = self.cache)

        assert x.render(cache = self.cache) == "<div>x</div>"

        x.cache_key = "a"
        assert x.render(cache = self.cache) == "<div>a</div>"

        x.cache_key = "b"
        assert x.render(cache = self.cache) == "<div>b</div>"

    def test_cached_content_respects_renderer_class(self):
        from cocktail.html.element import Element
        from cocktail.html.renderers import html4_renderer, xhtml_renderer

        img = Element("img")
        img.cached = True
        img.cache_key = "test"
        img.render(cache = self.cache)

        html = img.render(renderer = html4_renderer, cache = self.cache)
        assert html == "<img>"

        xhtml = img.render(renderer = xhtml_renderer, cache = self.cache)
        assert xhtml == "<img/>"

    def test_cached_content_includes_resources(self):

        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.cache_key = "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.add_resource("foo.js")
            e.append(child)

        e.render(cache = self.cache)

        assert "foo.js" in e.render_page()

    def test_cached_content_includes_client_parameters(self):

        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.cache_key = "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.set_client_param("foo", "bar")
            e.append(child)

        e.render(cache = self.cache)

        assert "foo" in e.render_page()

    def test_cached_content_includes_client_variables(self):

        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.cache_key = "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.set_client_variable("foo", "bar")
            e.append(child)

        e.render(cache = self.cache)

        assert "foo" in e.render_page()

    def test_cached_content_includes_head_elements(self):

        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.cache_key = "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.add_head_element(Element("foo"))
            e.append(child)

        e.render(cache = self.cache)

        assert "foo" in e.render_page()

    def test_cached_content_includes_meta_tags(self):

        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.cache_key = lambda: "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.set_meta("foo", "bar")
            e.append(child)

        e.render(cache = self.cache)

        assert "foo" in e.render_page()

    def test_cached_content_includes_client_translations(self):

        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.cache_key = "test"

        @e.when_ready
        def add_resources():
            child = Element()
            child.add_client_translation("foo")
            e.append(child)

        e.render(cache = self.cache)

        assert "foo" in e.render_page()

    def test_elements_can_define_cache_expiration(self):

        from time import sleep
        from datetime import timedelta
        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.cache_key = "test"
        e.cache_expiration = timedelta(seconds = 1)
        e.render(cache = self.cache)

        e.append("foo")
        assert "foo" not in e.render(cache = self.cache)

        sleep(1.2)
        assert "foo" in e.render(cache = self.cache)

    def test_elements_can_invalidate_cached_content(self):

        from cocktail.html.element import Element

        e = Element()
        e.cached = True
        e.cached_key = "foo"
        e.cache_tags.add("foo")
        e.render(cache = self.cache)

        e.append("foo")
        html = e.render(cache = self.cache)
        assert "foo" not in html

        self.cache.clear(scope = ["foo"])
        html = e.render(cache = self.cache)
        assert "foo" in html

