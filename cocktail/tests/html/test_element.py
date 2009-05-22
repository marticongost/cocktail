#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
from unittest import TestCase

class ElementAttributesTestCase(TestCase):

    def test_get_set(self):        
        
        from cocktail.html.element import Element        
        e = Element()
        
        # Attributes can be set and read
        e["id"] = "foo"
        e["title"] = "hello world"
        self.assertEquals(e["id"], "foo")
        self.assertEquals(e["title"], "hello world")
 
        # Attributes can be changed
        e["id"] = "bar"
        self.assertEquals(e["id"], "bar")

    def get_undefined(self):
        
        from cocktail.html.element import Element        
        e = Element()
        
        # Getting an undefined attribute yields None
        self.assertTrue(e["id"] is None)

    def test_set_none(self):
        
        from cocktail.html.element import Element
        
        e = Element()
        e["id"] = "foo"

        # Setting an attribute to None removes it from its element
        e["id"] = None
        self.assertFalse("id" in e.attributes)

    def test_delete(self):
        
        from cocktail.html.element import Element
        
        e = Element()
        e["id"] = "foo"

        # Deleting an attribute removes it from its element
        del e["id"]
        self.assertFalse("id" in e.attributes)

    def test_delete_undefined(self):
        
        from cocktail.html.element import Element
        e = Element()

        # Deleting an undefined attribute is a no-op
        del e["id"]
        self.assertFalse("id" in e.attributes)

    def test_constructor(self):

        from cocktail.html.element import Element

        # Attributes can be set using the element's constructor
        e = Element(id = "foo", title = "hello world")
        self.assertEquals(e["id"], "foo")
        self.assertEquals(e["title"], "hello world")

    def test_list(self):

        from cocktail.html.element import Element
        
        # An element starts with no attributes
        e = Element()
        self.assertEquals(e.attributes, {})

        # Attributes set on the element show on its 'attributes' collection
        e["id"] = "foo"
        e["title"] = "hello world"
        self.assertEquals(e.attributes, {"id": "foo", "title": "hello world"})

class ElementMetaAttributesTestCase(TestCase):

    def test_get_set(self):
        
        from cocktail.html.element import Element
        e = Element()
        
        # Meta attributes can be set and read
        e.set_meta("desc", "this is a test element")
        e.set_meta("keywords", "foo bar")
        self.assertEquals(e.get_meta("desc"), "this is a test element")
        self.assertEquals(e.get_meta("keywords"), "foo bar")
 
        # Meta attributes can be changed
        e.set_meta("keywords", "sprunge")
        self.assertEquals(e.get_meta("keywords"), "sprunge")

    def get_undefined(self):
        
        from cocktail.html.element import Element
        e = Element()
        
        # Getting an undefined meta attribute yields None
        self.assertTrue(e.get_meta("desc") is None)

    def test_set_none(self):
        
        from cocktail.html.element import Element
        
        e = Element()
        e.set_meta("desc", "foo")

        # Setting a meta attribute to None removes it from its element
        e.set_meta("desc", None)
        self.assertFalse("id" in e.meta)

    def test_constructor(self):

        from cocktail.html.element import Element

        # Attributes can be set using the element's constructor
        e = Element(id = "foo", title = "hello world")
        self.assertEquals(e["id"], "foo")
        self.assertEquals(e["title"], "hello world")

    def test_list(self):

        from cocktail.html.element import Element
        
        # An element starts with no meta attributes
        e = Element()
        self.assertEquals(e.meta, {})

        # Meta attributes set on the element show on its 'meta' collection
        e.set_meta("desc", "this is a test element")
        e.set_meta("keywords", "foo bar")
        self.assertEquals(e.meta, {
            "desc": "this is a test element",
            "keywords": "foo bar"
        })

class ElementVisibilityTestCase(TestCase):
    
    def test_visible_default(self):

        from cocktail.html.element import Element
        
        # Elements must be visible by default
        self.assertTrue(Element().visible)

    def test_visible_rendered(self):

        from cocktail.html.element import Element
        e = Element()

        # Visible elements should be rendered
        e.visible = True
        self.assertTrue(e.rendered)

        # Invisible elements shouldn't be rendered
        e.visible = False
        self.assertFalse(e.rendered)

    def test_collapsible_default(self):

        from cocktail.html.element import Element

        # By default, elements are not collapsible
        self.assertFalse(Element().collapsible)

    def test_collapsible_rendered(self):

        from cocktail.html.element import Element
        
        parent = Element()
        
        # An element starts with no rendered children
        self.assertFalse(parent.has_rendered_children())

        # A collapsible element with no children is not rendered
        parent.collapsible = True
        self.assertFalse(parent.rendered)

        # A collapsible element with visible children is rendered
        child1 = Element()
        parent.append(child1)
        self.assertTrue(parent.has_rendered_children())
        self.assertTrue(parent.rendered)

        # A collapsible element with invisible children is not rendered
        child1.visible = False
        self.assertFalse(parent.has_rendered_children())
        self.assertFalse(parent.rendered) 

        # A collapsible element with collapsible children without rendered
        # children is not rendered
        child1.visible = True
        child1.collapsible = True
        self.assertFalse(parent.has_rendered_children())
        self.assertFalse(parent.rendered)

        # The collapsible property applies recursively
        grandchild1 = Element()
        child1.append(grandchild1)
        self.assertTrue(parent.has_rendered_children())
        self.assertTrue(parent.rendered)
        self.assertTrue(child1.has_rendered_children())
        self.assertTrue(child1.rendered)

        grandchild1.visible = False
        self.assertFalse(parent.has_rendered_children())
        self.assertFalse(parent.rendered)
        self.assertFalse(child1.has_rendered_children())
        self.assertFalse(child1.rendered)

        # Just one rendered child suffices to get a collapsible element to be
        # rendered
        child2 = Element()
        parent.append(child2)
        self.assertTrue(parent.has_rendered_children())
        self.assertTrue(parent.rendered)

class ElementTreeTestCase(TestCase):

    def test_parent_is_readonly(self):

        from cocktail.html.element import Element
        e = Element()

        def set_parent():
            e.parent = None
        
        self.assertRaises(AttributeError, set_parent)

    def test_elements_start_empty(self):

        from cocktail.html.element import Element
        self.assertEqual(Element().children, [])

    def test_append(self):

        from cocktail.html.element import Element
        
        parent = Element()

        child1 = Element()
        parent.append(child1)
        self.assertTrue(child1.parent is parent)
        self.assertEquals(parent.children, [child1])

        child2 = Element()
        parent.append(child2)
        self.assertTrue(child2.parent is parent)
        self.assertEquals(parent.children, [child1, child2])

        child2.append(child1)
        self.assertTrue(child1.parent is child2)
        self.assertEquals(child2.children, [child1])

        parent.append(child1)
        self.assertTrue(child1.parent is parent)
        self.assertEquals(parent.children, [child2, child1])

    def test_append_content(self):

        from cocktail.html.element import Element, Content

        parent = Element()
        parent.append("hello world")

        self.assertEquals(len(parent.children), 1)
        child = parent.children[0]
        self.assertTrue(isinstance(child, Content))
        self.assertEquals(child.value, "hello world")
        self.assertTrue(child.parent is parent)

        parent = Element(children = ["hello world"])

        self.assertEquals(len(parent.children), 1)
        child = parent.children[0]
        self.assertTrue(isinstance(child, Content))
        self.assertEquals(child.value, "hello world")
        self.assertTrue(child.parent is parent)

    def test_insert(self):
        
        from cocktail.html.element import Element

        parent = Element()
        
        child1 = Element()
        parent.insert(0, child1)
        self.assertTrue(child1.parent is parent)
        self.assertEquals(parent.children, [child1])

        child2 = Element()
        parent.insert(1, child2)
        self.assertTrue(child2.parent is parent)
        self.assertEquals(parent.children, [child1, child2])

        child3 = Element()
        parent.insert(0, child3)
        self.assertTrue(child3.parent is parent)
        self.assertEquals(parent.children, [child3, child1, child2])

        child4 = Element()
        parent.insert(2, child4)
        self.assertTrue(child4.parent is parent)
        self.assertEquals(parent.children, [child3, child1, child4, child2])

        child5 = Element()
        parent.insert(-1, child5)
        self.assertTrue(child5.parent is parent)
        self.assertEquals(
            parent.children,
            [child3, child1, child4, child5, child2]
        )

        child6 = Element()
        parent.insert(5, child6)
        self.assertTrue(child6.parent is parent)
        self.assertEquals(
            parent.children,
            [child3, child1, child4, child5, child2, child6]
        )

    def test_insert_content(self):

        from cocktail.html.element import Element, Content

        parent = Element()
        parent.insert(0, "hello world")

        self.assertEquals(len(parent.children), 1)
        child = parent.children[0]
        self.assertTrue(isinstance(child, Content))
        self.assertEquals(child.value, "hello world")
        self.assertTrue(child.parent is parent)

    def test_place_before_root(self):
        
        from cocktail.html.element import Element, ElementTreeError

        def place_before_root():
            sibling = Element()
            e = Element()
            e.place_before(sibling)

        self.assertRaises(ElementTreeError, place_before_root)

    def test_place_before(self):

        from cocktail.html.element import Element

        parent = Element()
        child1 = Element()
        parent.append(child1)

        child2 = Element()
        child2.place_before(child1)
        self.assertTrue(child2.parent is parent)
        self.assertEquals(parent.children, [child2, child1])

        child3 = Element()
        child3.place_before(child1)
        self.assertTrue(child3.parent is parent)
        self.assertEquals(parent.children, [child2, child3, child1])

        child3.place_before(child2)
        self.assertTrue(child3.parent is parent)
        self.assertEquals(parent.children, [child3, child2, child1])

    def test_place_after_root(self):
        
        from cocktail.html.element import Element, ElementTreeError

        def place_after_root():
            sibling = Element()
            e = Element()
            e.place_after(sibling)

        self.assertRaises(ElementTreeError, place_after_root)

    def test_place_after(self):

        from cocktail.html.element import Element

        parent = Element()
        child1 = Element()
        parent.append(child1)

        child2 = Element()
        child2.place_after(child1)
        self.assertTrue(child2.parent is parent)
        self.assertEquals(parent.children, [child1, child2])

        child3 = Element()
        child3.place_after(child1)
        self.assertTrue(child3.parent is parent)
        self.assertEquals(parent.children, [child1, child3, child2])

        child3.place_after(child2)
        self.assertTrue(child3.parent is parent)
        self.assertEquals(parent.children, [child1, child2, child3])

    def test_place_before(self):
        pass

    def test_release(self):

        from cocktail.html.element import Element

        # Releasing a top-level element is a no-op
        parent = Element()
        parent.release()

        # Releasing a child element removes it from its parent
        child = Element()
        parent.append(child)
        child.release()
        self.assertTrue(child.parent is None)
        self.assertEquals(parent.children, [])

    def test_empty(self):

        from cocktail.html.element import Element

        parent = Element()
        
        # Emptying an empty element is a no-op
        parent.empty()

        # Emptying an element removes all its children
        child1 = Element()
        parent.append(child1)
        child2 = Element()
        parent.append(child2)
        parent.empty()
        self.assertEquals(parent.children, [])
        self.assertTrue(child1.parent is None)
        self.assertTrue(child2.parent is None)

class ElementCSSClassesTestCase(TestCase):

    def test_starts_without_classes(self):
        
        from cocktail.html.element import Element
        e = Element()
        self.assertEquals(e["class"], None)
        self.assertEquals(e.classes, [])

    def test_styled_class(self):

        from cocktail.html.element import Element

        class Foo(Element):
            pass

        foo = Foo()
        self.assertEquals(foo["class"], "Foo")

        class Bar(Element):
            styled_class = False

        bar = Bar()
        self.assertTrue(bar["class"] is None)

        class Sprunge(Foo):
            pass

        sprunge = Sprunge()
        self.assertEquals(sprunge["class"], "Foo Sprunge")

        class Spam(Element):
            pass

        class Scrum(Foo, Spam):
            pass

        scrum = Scrum()
        self.assertEquals(scrum["class"], "Spam Foo Scrum")

    def test_constructor(self):
        
        from cocktail.html.element import Element
        e = Element(class_name = "huge fugly")
        self.assertEquals(e["class"], "huge fugly")
        self.assertEquals(e.classes, ["huge", "fugly"])

    def test_set_attribute(self):
        
        from cocktail.html.element import Element
        
        e = Element()

        # Setting the 'class' attribute reflects on the element's 'classes'
        # property
        e["class"] = "craptastic"
        self.assertEquals(e["class"], "craptastic")
        self.assertEquals(e.classes, ["craptastic"])

        # Same test again, but this time with more than one class
        e["class"] = "craptastic shiny"
        self.assertEquals(e["class"], "craptastic shiny")
        self.assertEquals(e.classes, ["craptastic", "shiny"])

    def test_add_class(self):
        
        from cocktail.html.element import Element
        
        e = Element()
        
        # Adding a class works as expected
        e.add_class("craptastic")
        self.assertEquals(e["class"], "craptastic")
        self.assertEquals(e.classes, ["craptastic"])

        # Adding a second class works ok
        e.add_class("shiny")
        self.assertEquals(e["class"], "craptastic shiny")
        self.assertEquals(e.classes, ["craptastic", "shiny"])

        # Adding an existing class is a no-op
        e.add_class("shiny")
        self.assertEquals(e["class"], "craptastic shiny")
        self.assertEquals(e.classes, ["craptastic", "shiny"])

    def test_remove_class(self):
        
        from cocktail.html.element import Element
        
        e = Element()
        
        # Removing an undefined class is a no-op
        e.remove_class("big")
        
        e.add_class("craptastic")
        e.add_class("shiny")
        e.add_class("important")
        
        e.remove_class("shiny")
        self.assertEquals(e["class"], "craptastic important")
        self.assertEquals(e.classes, ["craptastic", "important"])

        e.remove_class("important")
        self.assertEquals(e["class"], "craptastic")
        self.assertEquals(e.classes, ["craptastic"])

        e.remove_class("craptastic")
        self.assertEquals(e["class"], None)
        self.assertEquals(e.classes, [])

class ElementStyleTestCase(TestCase):

    def test_get_set(self):
        
        from cocktail.html.element import Element
        e = Element()
        
        # Style declarations can be set and read
        e.set_style("font-weight", "bold")
        e.set_style("margin", "1em")
        self.assertEquals(e.get_style("font-weight"), "bold")
        self.assertEquals(e.get_style("margin"), "1em")
 
        # Style declarations can be changed
        e.set_style("font-weight", "normal")
        self.assertEquals(e.get_style("font-weight"), "normal")

    def get_undefined(self):
        
        from cocktail.html.element import Element
        e = Element()
        
        # Getting an undefined style declaration yields None
        self.assertTrue(e.get_style("font-weight") is None)

    def test_set_none(self):
        
        from cocktail.html.element import Element
        
        e = Element()
        e.set_style("font-weight", "bold")

        # Setting a meta attribute to None removes it from its element
        e.set_style("font-weight", None)
        self.assertFalse("font-weight" in e.style)

    def test_dict(self):

        from cocktail.html.element import Element
        
        # An element starts with no style declarations
        e = Element()
        self.assertEquals(e.style, {})

        # Style declarations set on the element show on its 'style' collection
        e.set_style("text-decoration", "underline")
        e.set_style("font-size", "2em")
        self.assertEquals(e.style, {
            "text-decoration": "underline",
            "font-size": "2em"
        })

    def test_attribute(self):

        from cocktail.html.element import Element

        e = Element()
        e.set_style("font-weight", "bold")
        self.assertEquals(e["style"], "font-weight: bold")

        e.set_style("font-style", "italic")
        self.assertEquals(
            set(e["style"].split("; ")),
            set(["font-weight: bold", "font-style: italic"])
        )

class ElementResourcesTestCase(TestCase):

    def test_starts_empty(self):        
        from cocktail.html.element import Element
        self.assertEquals(Element().resources, [])
        self.assertEquals(Element().resource_uris, set())

    def __test_create_resource_from_uri(self, uri, expected_type):
        from cocktail.html.resources import Resource        
        resource = Resource.from_uri(uri)
        self.assertEquals(resource.uri, uri)
        self.assertTrue(isinstance(resource, expected_type))

    def test_create_unknown_resource_from_uri(self):
        from cocktail.html.resources import Resource
        self.assertRaises(
            ValueError,
            Resource.from_uri, "foo.spamspamspamtonesofspam!!!")

    def test_create_script_from_uri(self):
        from cocktail.html.resources import Script
        self.__test_create_resource_from_uri("foo.js", Script)

    def test_create_stylesheet_from_uri(self):
        from cocktail.html.resources import StyleSheet
        self.__test_create_resource_from_uri("foo.css", StyleSheet)

    def __test_add_uri(self, uri, expected_type):
        
        from cocktail.html.element import Element
        
        e = Element()
        e.add_resource(uri)
        self.assertEquals(len(e.resources), 1)
        self.assertEquals(len(e.resource_uris), 1)

        resource = e.resources[0]
        self.assertEquals(resource.uri, uri)
        self.assertTrue(isinstance(resource, expected_type))
        self.assertTrue(e.resource_uris, set([uri]))

    def test_add_script_uri(self):
        from cocktail.html.resources import Script
        self.__test_add_uri("foo.js", Script)

    def test_add_stylesheet_uri(self):
        from cocktail.html.resources import StyleSheet
        self.__test_add_uri("foo.css", StyleSheet)

    def test_add_resource(self):
        
        from cocktail.html.element import Element
        from cocktail.html.resources import Resource

        e = Element()
        
        r1 = Resource("foo.js")
        e.add_resource(r1)
        self.assertEquals(e.resources, [r1])
        self.assertEquals(e.resource_uris, set(["foo.js"]))

        r2 = Resource("bar.js")
        e.add_resource(r2)
        self.assertEquals(e.resources, [r1, r2])
        self.assertEquals(e.resource_uris, set(["foo.js", "bar.js"]))

    def test_add_resource_without_uri(self):

        from cocktail.html.element import Element
        from cocktail.html.resources import Resource

        self.assertRaises(ValueError, Element().add_resource, Resource(None))

    def test_remove_uri(self):
        
        from cocktail.html.element import Element
        from cocktail.html.resources import Resource

        e = Element()
        
        r1 = Resource("foo.js")
        e.add_resource(r1)
        
        r2 = Resource("bar.js")
        e.add_resource(r2)

        r3 = Resource("spam.js")
        e.add_resource(r3)

        # Elements are correctly removed
        e.remove_resource("bar.js")
        self.assertEquals(e.resources, [r1, r3])
        self.assertEquals(e.resource_uris, set([r1.uri, r3.uri]))

        # Removing an undefined resource raises an exception
        def remove_undefined():
            e.remove_resource("bar.js")

        self.assertRaises(ValueError, remove_undefined)

        # Removing the remaining resources works ok
        e.remove_resource("foo.js")
        self.assertEquals(e.resources, [r3])
        self.assertEquals(e.resource_uris, set([r3.uri]))

        e.remove_resource("spam.js")
        self.assertEquals(e.resources, [])
        self.assertEquals(e.resource_uris, set())

    def test_remove_resource(self):
        
        from cocktail.html.element import Element
        from cocktail.html.resources import Resource

        e = Element()
        
        r1 = Resource("foo.js")
        e.add_resource(r1)
        
        r2 = Resource("bar.js")
        e.add_resource(r2)

        r3 = Resource("spam.js")
        e.add_resource(r3)

        # Elements are correctly removed
        e.remove_resource(r2)
        self.assertEquals(e.resources, [r1, r3])
        self.assertEquals(e.resource_uris, set([r1.uri, r3.uri]))

        # Removing an undefined resource raises an exception
        def remove_undefined():
            e.remove_resource(r2)

        self.assertRaises(ValueError, remove_undefined)

        # Removing the remaining resources works ok
        e.remove_resource(r1)
        self.assertEquals(e.resources, [r3])
        self.assertEquals(e.resource_uris, set([r3.uri]))

        e.remove_resource(r3)
        self.assertEquals(e.resources, [])
        self.assertEquals(e.resource_uris, set())

    def test_resource_set(self):
        
        from cocktail.html.element import Element
        from cocktail.html.resources import Resource, Script

        e = Element()
        r1 = Resource("foo.js")

        # Adding the same resource object twice only adds the resource once
        added = e.add_resource(r1)
        self.assertTrue(added)        
        added = e.add_resource(r1)
        self.assertFalse(added)
        self.assertEquals(e.resources, [r1])
        self.assertEquals(e.resource_uris, set([r1.uri]))

        # Adding a different resource object with the same resource URI adds a
        # single resource
        added = e.add_resource(Resource("foo.js"))
        self.assertFalse(added)
        self.assertEquals(e.resources, [r1])
        self.assertEquals(e.resource_uris, set([r1.uri]))

        # Again, a different resource object with the same URI, this time using
        # a different resource type; should get the same result.
        added = e.add_resource(Script("foo.js"))
        self.assertFalse(added)
        self.assertEquals(e.resources, [r1])
        self.assertEquals(e.resource_uris, set([r1.uri]))

        # Adding the same URI using a string is also ignored
        added = e.add_resource("foo.js")
        self.assertFalse(added)
        self.assertEquals(e.resources, [r1])
        self.assertEquals(e.resource_uris, set([r1.uri]))

    def test_set_resource_uri(self):
        
        from cocktail.html.resources import Resource
    
        # A resource's uri can be set through its constructor
        r = Resource("foo.js")
        self.assertEquals(r.uri, "foo.js")

        # But can't be changed afterwards
        def change_uri():
            r.uri = "bar.js"

        self.assertRaises(AttributeError, change_uri)

class ElementClientParamsTestCase(TestCase):

    def test_defaults(self):
        from cocktail.html.element import Element
        self.assertEquals(Element().client_params, {})

    def test_get_set(self):
        
        from cocktail.html.element import Element
        e = Element()

        e.set_client_param("foo", 3)
        self.assertEquals(e.get_client_param("foo"), 3)
        self.assertEquals(e.client_params, {"foo": 3})

        e.set_client_param("bar", "hello world")
        self.assertEquals(e.get_client_param("bar"), "hello world")
        self.assertEquals(e.client_params, {"foo": 3, "bar": "hello world"})

        e.set_client_param("foo", 12)
        self.assertEquals(e.get_client_param("foo"), 12)
        self.assertEquals(e.client_params, {"foo": 12, "bar": "hello world"})

    def test_get_undefined(self):
        from cocktail.html.element import Element
        self.assertRaises(KeyError, Element().get_client_param, "foo")

    def test_set_none(self):

        from cocktail.html.element import Element
        e = Element()
        e.set_client_param("foo", None)
        self.assertTrue(e.get_client_param("foo") is None)
        self.assertEquals(e.client_params, {"foo": None})

    def test_remove(self):

        from cocktail.html.element import Element
        e = Element()
        e.set_client_param("foo", 5)
        e.remove_client_param("foo")
        self.assertEquals(e.client_params, {})
        self.assertRaises(KeyError, e.get_client_param, "foo")
        self.assertRaises(KeyError, e.remove_client_param, "foo")

