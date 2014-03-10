#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from unittest import TestCase


class GenericMethodTestCase(TestCase):

    def test_default_implementation(self):

        from cocktail.modeling import GenericMethod

        class Foo(object):
            pass

        @GenericMethod
        def test_method(instance, param):
            self.assertTrue(instance is test_instance)
            param["value"] = "default"
            return "default"

        test_instance = Foo()
        test_param = {}
        rvalue = test_method(test_instance, test_param)
        
        self.assertEqual(test_param, {"value": "default"})
        self.assertEqual(rvalue, "default")

    def test_implementations(self):

        from cocktail.modeling import GenericMethod
        test = self

        @GenericMethod
        def test_method(instance, param):
            test.assertTrue(instance is spam)
            param["value"] = "default"
            return "default"

        # Custom implementation #1
        class Foo(object):
        
            def foo_test_method(self, param):
                test.assertTrue(self is foo)
                param["value"] = "foo"
                return "foo"
        
        test_method.implementations[Foo] = Foo.foo_test_method

        # Custom implementation #2
        class Bar(object):
            
            def bar_test_method(self, param):
                test.assertTrue(self is bar)
                param["value"] = "bar"
                return "bar"

        test_method.implementations[Bar] = Bar.bar_test_method

        # This class doesn't implement the method, it should use the default
        # implementation
        class Spam(object):
            pass

        foo = Foo()
        bar = Bar()
        spam = Spam()

        test_param = {}
        rvalue = test_method(foo, test_param)
        self.assertEqual(test_param, {"value": "foo"})
        self.assertEqual(rvalue, "foo")

        test_param = {}
        rvalue = test_method(bar, test_param)
        self.assertEqual(test_param, {"value": "bar"})
        self.assertEqual(rvalue, "bar")

        test_param = {}
        rvalue = test_method(spam, test_param)
        self.assertEqual(test_param, {"value": "default"})
        self.assertEqual(rvalue, "default")

    def test_inheritance(self):

        from cocktail.modeling import GenericMethod
        test = self

        @GenericMethod
        def test_method(instance, param):
            raise TypeError(
                    "%s doesn't provide an implementation for the "
                    "requested generic method" % instance)
        
        class Base(object):
        
            def base_test_method(self, param):
                param["value"] = "base"
                return "base"

        test_method.implementations[Base] = Base.base_test_method

        class Derived1(Base):

            def derived_test_method(self, param):
                param["value"] = "derived1"
                return "derived1"

        test_method.implementations[Derived1] = Derived1.derived_test_method
        
        class Derived2(Base):
            pass

        base = Base()
        derived1 = Derived1()
        derived2 = Derived2()

        test_param = {}
        rvalue = test_method(base, test_param)
        self.assertEqual(test_param, {"value": "base"})
        self.assertEqual(rvalue, "base")

        test_param = {}
        rvalue = test_method(derived1, test_param)
        self.assertEqual(test_param, {"value": "derived1"})
        self.assertEqual(rvalue, "derived1")

        test_param = {}
        rvalue = test_method(derived2, test_param)
        self.assertEqual(test_param, {"value": "base"})
        self.assertEqual(rvalue, "base")


class OrderedDictTestCase(TestCase):

    pairs = [
        ("Chuck", "Norris"),
        ("Steven", "Seagal"),
        ("Kurt", "Russell")
    ]

    def assert_order(self, dictionary, pairs):
        
        ordered_keys = [key for key, value in pairs]
        ordered_values = [value for key, value in pairs]

        assert list(dictionary) == ordered_keys
        assert dictionary.keys() == ordered_keys
        assert list(dictionary.iterkeys()) == ordered_keys

        assert dictionary.values() == ordered_values
        assert list(dictionary.itervalues()) == ordered_values

        assert dictionary.items() == pairs
        assert list(dictionary.iteritems()) == pairs

    def test_constructor(self):
        from cocktail.modeling import OrderedDict
        d = OrderedDict(self.pairs)
        self.assert_order(d, self.pairs)

    def test_set_item(self):
        from cocktail.modeling import OrderedDict
        d = OrderedDict()
                
        for key, value in self.pairs:
            d[key] = value

        self.assert_order(d, self.pairs)

    def test_update(self):
        from cocktail.modeling import OrderedDict
        d = OrderedDict()
        d.update(self.pairs)
        self.assert_order(d, self.pairs)

    def test_delete(self):
        from cocktail.modeling import OrderedDict
        d = OrderedDict(self.pairs)
        del d["Steven"]
        self.assert_order(d, [("Chuck", "Norris"), ("Kurt", "Russell")])

    def test_pop(self):
        from cocktail.modeling import OrderedDict
        d = OrderedDict(self.pairs)
        value = d.pop("Steven")
        assert value == "Seagal"
        self.assert_order(d, [("Chuck", "Norris"), ("Kurt", "Russell")])

