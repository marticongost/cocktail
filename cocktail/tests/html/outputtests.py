#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
from unittest import TestCase

class HTML4RendererTestCase(TestCase):

    def get_html(self, element, full_page = False):
        
        from cocktail.html.renderers import HTML4Renderer
        renderer = HTML4Renderer()
        
        if full_page:
            return element.render_page(renderer)
        else:
            return element.render(renderer)

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

    def get_test_tree_html(self, full_page = False):

        body = (
            '<div>'
                '<p>'
                    '<img src="foo.png">'
                    '<a href="http://www.foo.com">Foo!</a>'
                '</p>'
                '<p>The best <em>foo</em> in town!</p>'
            '</div>'
        )

        if full_page:
            return '<html><head></head><body>%s</body></html>' % body
        else:
            return body

    def test_void_element(self):        
        from cocktail.html.element import Element
        e = Element()
        e.tag = None
        self.assertEquals(self.get_html(e), u"")

    def test_content(self):
        from cocktail.html.element import Content     
        e = Content("hello world")
        self.assertEquals(self.get_html(e), u"hello world")

    def test_invisible_element_not_rendered(self):
        
        from cocktail.html.element import Element
        
        e = Element()
        e.visible = False
        self.assertEquals(self.get_html(e), u"")

        e.visible = True
        e.collapsible = True
        self.assertEquals(self.get_html(e), u"")

        child = Element()
        child.visible = False
        e.append(child)
        self.assertEquals(self.get_html(e), u"")

    def test_empty_single_elements(self):
        
        from cocktail.html.element import Element

        for tag in (u"img", u"link", u"hr", u"br"):            
            e = Element()
            e.tag = tag
            self.assertEquals(self.get_html(e), u"<%s>" % tag)

    def test_empty_compound_elements(self):

        from cocktail.html.element import Element

        for tag in (u"div", u"script", u"table", u"p", u"b"):
            e = Element()
            e.tag = tag            
            self.assertEquals(self.get_html(e), u"<%s></%s>" % (tag, tag))

    def test_empty_single_elements_with_attributes(self):

        from cocktail.html.element import Element

        for tag in (u"img", u"link", u"hr", u"br"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            self.assertEquals(
                self.get_html(e),
                u'<%s title="hello world">' % tag
            )

        for tag in (u"img", u"link", u"hr", u"br"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == u'<%s title="hello world" id="foo">' % tag
                or html == u'<%s id="foo" title="hello world">' % tag
            )

        for tag in (u"img", u"link", u"hr", u"br"):            
            e = Element()
            e.tag = tag
            e["selected"] = True
            e["checked"] = False
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == u'<%s selected id="foo">' % tag
                or html == u'<%s id="foo" selected>' % tag
            )

    def test_empty_compound_elements_with_attributes(self):

        from cocktail.html.element import Element

        for tag in (u"div", u"script", u"table", u"p", u"b"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            self.assertEquals(
                self.get_html(e),
                u'<%s title="hello world"></%s>' % (tag, tag)
            )
        
        for tag in (u"div", u"script", u"table", u"p", u"b"):
            e = Element()
            e.tag = tag
            e["selected"] = True
            e["checked"] = False
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == u'<%s selected id="foo"></%s>' % (tag, tag)
                or 
                html == u'<%s id="foo" selected></%s>' % (tag, tag)
            )

        for tag in (u"div", u"script", u"table", u"p", u"b"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == u'<%s title="hello world" id="foo"></%s>' % (tag, tag)
                or 
                html == u'<%s id="foo" title="hello world"></%s>' % (tag, tag)
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
        self.assertEquals(self.get_html(tree), self.get_test_tree_html())
    
#    def test_render_page(self):        
#        
#        from cocktail.html.renderers import HTML4Renderer
#        
#        tree = self.get_test_tree()
#        
#        renderer = HTML4Renderer()
#        renderer.doctype = None

#        self.assertEquals(
#            tree.render_page(renderer),
#            self.get_test_tree_html(full_page = True))


class XHTMLRendererTestCase(TestCase):

    def get_html(self, element):
        from cocktail.html.renderers import XHTMLRenderer
        return element.render(XHTMLRenderer())

    def test_void_element(self):        
        from cocktail.html.element import Element        
        e = Element()
        e.tag = None
        self.assertEquals(self.get_html(e), u"")

    def test_content(self):
        from cocktail.html.element import Content     
        e = Content("hello world")
        self.assertEquals(self.get_html(e), u"hello world")

    def test_invisible_element_not_rendered(self):
        
        from cocktail.html.element import Element
        
        e = Element()
        e.visible = False
        self.assertEquals(self.get_html(e), u"")

        e.visible = True
        e.collapsible = True
        self.assertEquals(self.get_html(e), u"")

        child = Element()
        child.visible = False
        e.append(child)
        self.assertEquals(self.get_html(e), u"")

    def test_empty_single_elements(self):
        
        from cocktail.html.element import Element

        for tag in (u"img", u"link", u"hr", u"br"):            
            e = Element()
            e.tag = tag
            self.assertEquals(self.get_html(e), u"<%s/>" % tag)

    def test_empty_compound_elements(self):

        from cocktail.html.element import Element

        for tag in (u"div", u"script", u"table", u"p", u"b"):
            e = Element()
            e.tag = tag            
            self.assertEquals(self.get_html(e), u"<%s></%s>" % (tag, tag))

    def test_empty_single_elements_with_attributes(self):

        from cocktail.html.element import Element

        for tag in (u"img", u"link", u"hr", u"br"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            self.assertEquals(
                self.get_html(e),
                u'<%s title="hello world"/>' % tag
            )

        for tag in (u"img", u"link", u"hr", u"br"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == u'<%s title="hello world" id="foo"/>' % tag
                or html == u'<%s id="foo" title="hello world"/>' % tag
            )

        for tag in (u"img", u"link", u"hr", u"br"): 
            e = Element()
            e.tag = tag
            e["selected"] = True
            e["checked"] = False
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == u'<%s selected="selected" id="foo"/>' % tag
                or html == u'<%s id="foo" selected="selected"/>' % tag
            )

    def test_empty_compound_elements_with_attributes(self):

        from cocktail.html.element import Element

        for tag in (u"div", u"script", u"table", u"p", u"b"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            self.assertEquals(
                self.get_html(e),
                u'<%s title="hello world"></%s>' % (tag, tag)
            )
        
        for tag in (u"div", u"script", u"table", u"p", u"b"):
            e = Element()
            e.tag = tag
            e["selected"] = True
            e["checked"] = False
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == u'<%s selected="selected" id="foo"></%s>' % (tag, tag)
                or 
                html == u'<%s id="foo" selected="selected"></%s>' % (tag, tag)
            )

        for tag in (u"div", u"script", u"table", u"p", u"b"):
            e = Element()
            e.tag = tag
            e["title"] = "hello world"
            e["id"] = "foo"
            html = self.get_html(e)
            self.assertTrue(
                html == u'<%s title="hello world" id="foo"></%s>' % (tag, tag)
                or 
                html == u'<%s id="foo" title="hello world"></%s>' % (tag, tag)
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
        
        self.assertEquals(
            html,
            '<div>'
                '<p>'
                    '<img src="foo.png"/>'
                    '<a href="http://www.foo.com">Foo!</a>'
                '</p>'
                '<p>The best <em>foo</em> in town!</p>'
            '</div>'
        )

