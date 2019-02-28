#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
from unittest import TestCase

class HTML4RendererTestCase(TestCase):

    def get_html(self, element):
        from cocktail.html.renderers import html4_renderer
        return element.render(renderer = html4_renderer)

    def get_test_tree(self):

        from cocktail.html.element import Element

        return Element(
            tag = "div",
            children = [
                Element("p", children = [
                    Element("img", src = "foo.png"),
                    Element("a", href = "http://www.foo.com", children = [
                        "Foo!"
                    ])
                ]),
                Element("p", children = [
                    "The best ",
                    Element("em", children = ["foo"]),
                    " in town!"
                ])
            ]
        )

    def get_test_tree_html(self):
        return (
            '<div>'
                '<p>'
                    '<img src="foo.png">'
                    '<a href="http://www.foo.com">Foo!</a>'
                '</p>'
                '<p>The best <em>foo</em> in town!</p>'
            '</div>'
        )

    def test_void_element(self):
        from cocktail.html.element import Element
        e = Element()
        e.tag = None
        self.assertEqual(self.get_html(e), "")

    def test_content(self):
        from cocktail.html.element import Content
        e = Content("hello world")
        self.assertEqual(self.get_html(e), "hello world")

    def test_invisible_element_not_rendered(self):

        from cocktail.html.element import Element

        e = Element()
        e.visible = False
        self.assertEqual(self.get_html(e), "")

        e.visible = True
        e.collapsible = True
        self.assertEqual(self.get_html(e), "")

        child = Element()
        child.visible = False
        e.append(child)
        self.assertEqual(self.get_html(e), "")

    def test_empty_single_elements(self):

        from cocktail.html.element import Element

        for tag in ("img", "link", "hr", "br"):
            e = Element()
            e.tag = tag
            self.assertEqual(self.get_html(e), "<%s>" % tag)

    def test_empty_compound_elements(self):

        from cocktail.html.element import Element

        for tag in ("div", "script", "table", "p", "b"):
            e = Element()
            e.tag = tag
            self.assertEqual(self.get_html(e), "<%s></%s>" % (tag, tag))

    def test_empty_single_elements_with_attributes(self):

        from cocktail.html.element import Element

        for tag in ("img", "link", "hr", "br"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            self.assertEqual(
                self.get_html(e),
                '<%s title="hello world">' % tag
            )

        for tag in ("img", "link", "hr", "br"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == '<%s title="hello world" id="foo">' % tag
                or html == '<%s id="foo" title="hello world">' % tag
            )

        for tag in ("img", "link", "hr", "br"):
            e = Element()
            e.tag = tag
            e["selected"] = True
            e["checked"] = False
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == '<%s selected id="foo">' % tag
                or html == '<%s id="foo" selected>' % tag
            )

    def test_empty_compound_elements_with_attributes(self):

        from cocktail.html.element import Element

        for tag in ("div", "script", "table", "p", "b"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            self.assertEqual(
                self.get_html(e),
                '<%s title="hello world"></%s>' % (tag, tag)
            )

        for tag in ("div", "script", "table", "p", "b"):
            e = Element()
            e.tag = tag
            e["selected"] = True
            e["checked"] = False
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == '<%s selected id="foo"></%s>' % (tag, tag)
                or
                html == '<%s id="foo" selected></%s>' % (tag, tag)
            )

        for tag in ("div", "script", "table", "p", "b"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == '<%s title="hello world" id="foo"></%s>' % (tag, tag)
                or
                html == '<%s id="foo" title="hello world"></%s>' % (tag, tag)
            )

    def test_single_elements_with_children(self):

        from cocktail.html.element import Element
        from cocktail.html.renderers import HTML4Renderer, RenderingError

        e = Element("img")
        e.append(Element())
        self.assertRaises(RenderingError, e.render, HTML4Renderer())

    def test_element_tree(self):
        tree = self.get_test_tree()
        html = self.get_html(tree)
        self.assertEqual(self.get_html(tree), self.get_test_tree_html())


class XHTMLRendererTestCase(TestCase):

    def get_html(self, element):
        from cocktail.html.renderers import xhtml_renderer
        return element.render(renderer = xhtml_renderer)

    def test_void_element(self):
        from cocktail.html.element import Element
        e = Element()
        e.tag = None
        self.assertEqual(self.get_html(e), "")

    def test_content(self):
        from cocktail.html.element import Content
        e = Content("hello world")
        self.assertEqual(self.get_html(e), "hello world")

    def test_invisible_element_not_rendered(self):

        from cocktail.html.element import Element

        e = Element()
        e.visible = False
        self.assertEqual(self.get_html(e), "")

        e.visible = True
        e.collapsible = True
        self.assertEqual(self.get_html(e), "")

        child = Element()
        child.visible = False
        e.append(child)
        self.assertEqual(self.get_html(e), "")

    def test_empty_single_elements(self):

        from cocktail.html.element import Element

        for tag in ("img", "link", "hr", "br"):
            e = Element()
            e.tag = tag
            self.assertEqual(self.get_html(e), "<%s/>" % tag)

    def test_empty_compound_elements(self):

        from cocktail.html.element import Element

        for tag in ("div", "script", "table", "p", "b"):
            e = Element()
            e.tag = tag
            self.assertEqual(self.get_html(e), "<%s></%s>" % (tag, tag))

    def test_empty_single_elements_with_attributes(self):

        from cocktail.html.element import Element

        for tag in ("img", "link", "hr", "br"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            self.assertEqual(
                self.get_html(e),
                '<%s title="hello world"/>' % tag
            )

        for tag in ("img", "link", "hr", "br"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == '<%s title="hello world" id="foo"/>' % tag
                or html == '<%s id="foo" title="hello world"/>' % tag
            )

        for tag in ("img", "link", "hr", "br"):
            e = Element()
            e.tag = tag
            e["selected"] = True
            e["checked"] = False
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == '<%s selected="selected" id="foo"/>' % tag
                or html == '<%s id="foo" selected="selected"/>' % tag
            )

    def test_empty_compound_elements_with_attributes(self):

        from cocktail.html.element import Element

        for tag in ("div", "script", "table", "p", "b"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            self.assertEqual(
                self.get_html(e),
                '<%s title="hello world"></%s>' % (tag, tag)
            )

        for tag in ("div", "script", "table", "p", "b"):
            e = Element()
            e.tag = tag
            e["selected"] = True
            e["checked"] = False
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == '<%s selected="selected" id="foo"></%s>' % (tag, tag)
                or
                html == '<%s id="foo" selected="selected"></%s>' % (tag, tag)
            )

        for tag in ("div", "script", "table", "p", "b"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == '<%s title="hello world" id="foo"></%s>' % (tag, tag)
                or
                html == '<%s id="foo" title="hello world"></%s>' % (tag, tag)
            )

    def test_single_elements_with_children(self):

        from cocktail.html.element import Element
        from cocktail.html.renderers import HTML4Renderer, RenderingError

        e = Element("img")
        e.append(Element())
        self.assertRaises(RenderingError, e.render, HTML4Renderer())

    def test_element_tree(self):

        from cocktail.html.element import Element

        tree = Element(
            tag = "div",
            children = [
                Element("p", children = [
                    Element("img", src = "foo.png"),
                    Element("a", href = "http://www.foo.com", children = [
                        "Foo!"
                    ])
                ]),
                Element("p", children = [
                    "The best ",
                    Element("em", children = ["foo"]),
                    " in town!"
                ])
            ]
        )

        html = self.get_html(tree)

        self.assertEqual(
            html,
            '<div>'
                '<p>'
                    '<img src="foo.png"/>'
                    '<a href="http://www.foo.com">Foo!</a>'
                '</p>'
                '<p>The best <em>foo</em> in town!</p>'
            '</div>'
        )

