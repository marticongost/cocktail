#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class MemberQueryTestCase(TempStorageMixin, TestCase):

    def assert_queries(self, member, values, *tests):
        
        from cocktail.persistence import PersistentObject, datastore

        datastore.root.clear()

        if member.schema is None:
            class T(PersistentObject):
                i = None

                def __repr__(self):
                    return "%d:%s" % (self.i, self.m.encode("utf-8"))
            
            member.name = "m"
            T.add_member(member)
        else:
            T = member.schema

        instances = []

        for i, value in enumerate(values):
            instance = T()
            instance.i = i
            instance.m = value
            instance.insert()
            instances.append(instance)

        for expr, expected_results in tests:
            query = T.select(expr)
            self.assertEqual(
                set(query),
                set(instances[i] for i in expected_results)
            )
            self.assertEqual(len(query), len(expected_results))
    
    def test_equal(self):        
        
        from cocktail.schema import String

        # Search without duplicates
        m = String(unique = True, indexed = True, required = True)

        self.assert_queries(
            m,
            [u"foo", u"bar", u"scrum", u"sprunge"],
            (m.equal(u"zing"), []),
            (m.equal(u"FOO"), []),
            (m.equal(u"foo"), [0]),
            (m.equal(u"scrum"), [2])
        )
        
        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)
            
            self.assert_queries(
                m,
                [u"foo", u"foo", u"bar", u"scrum", u"sprunge", u"sprunge"],
                (m.equal(u"zing"), []),
                (m.equal(u"FOO"), []),
                (m.equal(u"foo"), [0, 1]),
                (m.equal(u"sprunge"), [-2, -1]),
                (m.equal(u"scrum"), [3])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)

        self.assert_queries(
            m,
            [u"foo", u"Foo", u"Foó"],
            (m.equal(u"FOO"), [0, 1, 2])
        )

    def test_not_equal(self):  
        
        from cocktail.schema import String
        
        # Search without duplicates
        m = String(unique = True, indexed = True, required = True)

        self.assert_queries(
            m,
            [u"foo"],
            (m.not_equal(u"foo"), [])
        )

        self.assert_queries(
            m,
            [u"foo", u"bar", u"scrum", u"sprunge"],
            (m.not_equal(u"zing"), [0, 1, 2, 3]),
            (m.not_equal(u"foo"), [1, 2, 3]),
            (m.not_equal(u"scrum"), [0, 1, 3])
        )
        
        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)
            
            self.assert_queries(
                m,
                [u"foo", u"foo", u"bar", u"scrum", u"sprunge", u"sprunge"],
                (m.not_equal(u"zing"), [0, 1, 2, 3, 4, 5]),
                (m.not_equal(u"foo"), [2, 3, 4, 5]),
                (m.not_equal(u"sprunge"), [0, 1, 2, 3]),
                (m.not_equal(u"scrum"), [0, 1, 2, 4, 5])
            )
        
        # Normalized string index
        m = String(indexed = True, normalized_index = True)

        self.assert_queries(
            m,
            [u"foo", u"Foo", u"Foó"],
            (m.not_equal(u"FOO"), []),
            (m.not_equal(u"bar"), [0, 1, 2])
        )

    def test_greater(self):

        from cocktail.schema import String

        # Search without duplicates
        m = String(unique = True, indexed = True, required = True)

        self.assert_queries(
            m,
            [u"foo", u"bar", u"scrum", u"SCRUM"],
            (m.greater(u"zing"), []),
            (m.greater(u"foo"), [2]),
            (m.greater(u"A"), [0, 1, 2, 3])
        )
        
        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)
            
            self.assert_queries(
                m,
                [u"foo", u"FOO", u"bar", u"scrum", u"sprunge", u"sprunge"],
                (m.greater(u"zing"), []),
                (m.greater(u"foo"), [3, 4, 5]),
                (m.greater(u"scrum"), [4, 5]),
                (m.greater(u"A"), [0, 1, 2, 3, 4, 5])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)
        
        self.assert_queries(
            m,
            [u"foo", u"Foo", u"Foó", u"bàr", u"BaR", u"bÄr"],
            (m.greater(u"A"), [0, 1, 2, 3, 4, 5]),
            (m.greater(u"a"), [0, 1, 2, 3, 4, 5]),
            (m.greater(u"f"), [0, 1, 2])
        )

    def test_greater_equal(self):

        from cocktail.schema import String

        # Search without duplicates
        m = String(unique = True, indexed = True, required = True)

        self.assert_queries(
            m,
            [u"foo", u"bar", u"scrum", u"SCRUM"],
            (m.greater_equal(u"zing"), []),
            (m.greater_equal(u"foo"), [0, 2]),
            (m.greater_equal(u"A"), [0, 1, 2, 3])
        )
        
        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)
            
            self.assert_queries(
                m,
                [u"foo", u"FOO", u"bar", u"scrum", u"sprunge", u"sprunge"],
                (m.greater_equal(u"zing"), []),
                (m.greater_equal(u"foo"), [0, 3, 4, 5]),
                (m.greater_equal(u"scrum"), [3, 4, 5]),
                (m.greater_equal(u"A"), [0, 1, 2, 3, 4, 5])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)
        
        self.assert_queries(
            m,
            [u"foo", u"Foo", u"Foó", u"bàr", u"BaR", u"bÄr"],
            (m.greater_equal(u"bar"), [0, 1, 2, 3, 4, 5]),
            (m.greater_equal(u"BAR"), [0, 1, 2, 3, 4, 5]),
            (m.greater_equal(u"foo"), [0, 1, 2]),
            (m.greater_equal(u"FOO"), [0, 1, 2])
        )

    def test_lower(self):

        from cocktail.schema import String

        # Search without duplicates
        m = String(unique = True, indexed = True, required = True)

        self.assert_queries(
            m,
            [u"foo", u"bar", u"scrum", u"SCRUM"],
            (m.lower(u"zing"), [0, 1, 2, 3]),
            (m.lower(u"scrum"), [0, 1, 3]),
            (m.lower(u"A"), [])
        )
        
        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)
            
            self.assert_queries(
                m,
                [u"foo", u"FOO", u"bar", u"scrum", u"sprunge", u"sprunge"],
                (m.lower(u"zing"), [0, 1, 2, 3, 4, 5]),
                (m.lower(u"foo"), [1, 2]),
                (m.lower(u"A"), [])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)
        
        self.assert_queries(
            m,
            [u"foo", u"Foo", u"Foó", u"bàr", u"BaR", u"bÄr"],
            (m.lower(u"Z"), [0, 1, 2, 3, 4, 5]),
            (m.lower(u"z"), [0, 1, 2, 3, 4, 5]),
            (m.lower(u"f"), [3, 4, 5])
        )

    def test_lower_equal(self):

        from cocktail.schema import String

        # Search without duplicates
        m = String(unique = True, indexed = True, required = True)

        self.assert_queries(
            m,
            [u"foo", u"bar", u"scrum", u"SCRUM"],
            (m.lower_equal(u"zing"), [0, 1, 2, 3]),
            (m.lower_equal(u"foo"), [0, 1, 3]),
            (m.lower_equal(u"A"), [])
        )
        
        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)
            
            self.assert_queries(
                m,
                [u"foo", u"FOO", u"bar", u"scrum", u"sprunge", u"sprunge"],
                (m.lower_equal(u"zing"), [0, 1, 2, 3, 4, 5]),
                (m.lower_equal(u"foo"), [0, 1, 2]),
                (m.lower_equal(u"A"), [])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)
        
        self.assert_queries(
            m,
            [u"foo", u"Foo", u"Foó", u"bàr", u"BaR", u"bÄr"],
            (m.lower_equal(u"bar"), [3, 4, 5]),
            (m.lower_equal(u"BÀR"), [3, 4, 5]),
            (m.lower_equal(u"foo"), [0, 1, 2, 3, 4, 5]),
            (m.lower_equal(u"FOO"), [0, 1, 2, 3, 4, 5])
        )

class OrderTestCase(TempStorageMixin, TestCase):

    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail.schema import String, Integer, Boolean
        from cocktail.persistence import PersistentObject

        class Product(PersistentObject):
            product_name = String(
                unique = True,
                indexed = True,
                required = True
            )
            price = Integer(indexed = True)
            category = String(indexed = True)
            color = String()
            available = Boolean()
        
        self.Product = Product

    def match(self, results, *group):        
        results_group = set(results.pop(0) for i in range(len(group)))
        self.assertEqual(results_group, set(group))

    def test_id(self):

        products = [self.Product() for i in range(10)]
        for product in products:
            product.insert()
        
        results = [product for product in self.Product.select(order = "id")]
        self.assertEqual(products, results)

        results = [product for product in self.Product.select(order = "-id")]
        results.reverse()
        self.assertEqual(products, results)

    def test_indexed_member_and_id(self):

        a = self.Product()
        a.price = 3
        a.insert()

        b = self.Product()
        b.price = 5
        b.insert()

        c = self.Product()
        c.price = 4
        c.insert()

        d = self.Product()
        d.price = 3
        d.insert()

        e = self.Product()
        e.price = 4
        e.insert()

        f = self.Product()
        f.price = None
        f.insert()

        results = [product
                   for product in self.Product.select(
                       order = ("price", "id"))]
        
        self.assertEqual([f, a, d, c, e, b], results)

        results = [product
                   for product in self.Product.select(
                       order = ("price", "-id"))]

        self.assertEqual([f, d, a, e, c, b], results)

        results = [product
                   for product in self.Product.select(
                       order = ("-price", "id"))]

        self.assertEqual([b, c, e, a, d, f], results)

        results = [product
                   for product in self.Product.select(
                       order = ("-price", "-id"))]

        self.assertEqual([b, e, c, d, a, f], results)

    def test_single_indexed_unique_member(self):
 
        a = self.Product()
        a.product_name = u"Wine"
        a.insert()

        b = self.Product()
        b.product_name = u"Cheese"
        b.insert()

        c = self.Product()
        c.product_name = u"Ham"
        c.insert()

        d = self.Product()
        d.product_name = u"Eggs"
        d.insert()

        e = self.Product()
        e.insert()

        results = [product
                   for product in self.Product.select(order = "product_name")]
        self.assertEqual([e, b, d, c, a], results)

        results = [product
                   for product in self.Product.select(order = "-product_name")]
        results.reverse()
        self.assertEqual([e, b, d, c, a], results)

    def test_multiple_indexed_members(self):

        a = self.Product()
        a.price = 3
        a.category = "sports"
        a.insert()

        b = self.Product()
        b.price = 5
        b.category = "food"
        b.insert()

        c = self.Product()
        c.price = 4
        c.category = "music"
        c.insert()

        d = self.Product()
        d.price = 3
        d.category = "music"
        d.insert()

        e = self.Product()
        e.price = 10
        e.category = "sports"
        e.insert()

        f = self.Product()
        f.price = None
        f.category = "food"
        f.insert()

        results = [product
                   for product in self.Product.select(
                       order = ("category", "price"))]
        
        self.assertEqual([f, b, d, c, a, e], results)

        results = [product
                   for product in self.Product.select(
                       order = ("category", "-price"))]

        self.assertEqual([b, f, c, d, e, a], results)

        results = [product
                   for product in self.Product.select(
                       order = ("-category", "price"))]

        self.assertEqual([a, e, d, c, f, b], results)

        results = [product
                   for product in self.Product.select(
                       order = ("-category", "-price"))]

        self.assertEqual([e, a, c, d, b, f], results)

    def test_single_not_indexed_member(self):

        a = self.Product()
        a.color = "red"
        a.insert()

        b = self.Product()
        b.color = "green"
        b.insert()

        c = self.Product()
        c.color = "blue"
        c.insert()

        d = self.Product()
        d.color = "green"
        d.insert()

        e = self.Product()
        e.color = "red"
        e.insert()

        f = self.Product()
        f.color = "blue"
        f.insert()

        results = [product for product in self.Product.select(order = "color")]
        self.match(results, c, f)
        self.match(results, b, d)
        self.match(results, a, e)

        results = [product
                   for product in self.Product.select(order = "-color")]
        self.match(results, a, e)
        self.match(results, b, d)
        self.match(results, c, f)

    def test_indexed_and_not_indexed_members(self):

        a = self.Product()
        a.color = "red"
        a.price = 10
        a.insert()

        b = self.Product()
        b.color = "green"
        b.price = 3
        b.insert()

        c = self.Product()
        c.color = "blue"
        c.price = 7
        c.insert()

        d = self.Product()
        d.color = "green"
        d.price = 5
        d.insert()

        e = self.Product()
        e.color = "red"
        e.price = 15
        e.insert()

        f = self.Product()
        f.color = "blue"
        f.price = 12
        f.insert()

        results = [product
                  for product in self.Product.select(
                      order = ("color", "price"))]
        self.assertEqual([c, f, b, d, a, e], results)

        results = [product
                   for product in self.Product.select(
                       order = ("color", "-price"))]
        self.assertEqual([f, c, d, b, e, a], results)

        results = [product
                   for product in self.Product.select(
                       order = ("-color", "price"))]
        self.assertEqual([a, e, b, d, c, f], results)

        results = [product
                   for product in self.Product.select(
                       order = ("-color", "-price"))]
        self.assertEqual([e, a, d, b, f, c], results)

    def test_normalized_index(self):
        
        self.Product.product_name.normalized_index = True

        a = self.Product()
        a.product_name = u"Àbac"
        a.insert()

        b = self.Product()
        b.product_name = u"alfombra"
        b.insert()

        results = [product
                for product in self.Product.select(order = "product_name")]
        
        self.assertEqual([a, b], results)


class RelationalQueriesTestCase(TempStorageMixin, TestCase):
           
    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail.schema import (
            String, Integer, Boolean, Reference, Collection
        )
        from cocktail.persistence import PersistentObject

        class Category(PersistentObject):            
            category_name = String()
            enabled = Boolean()
            products = Collection(bidirectional = True)

            def __repr__(self):
                return self.category_name

        class Product(PersistentObject):
            product_name = String()
            price = Integer()
            stock = Integer()
            category = Reference(bidirectional = True)
            orders = Collection(bidirectional = True)

            def __repr__(self):
                return self.product_name

        class Order(PersistentObject):
            quantity = Integer()
            product = Reference(bidirectional = True)

        Category.products.items = Reference(type = Product)
        Product.category.type = Category
        Product.orders.items = Reference(type = Order)
        Order.product.type = Product

        self.Category = Category
        self.Product = Product
        self.Order = Order

        self.categories = [
            Category(category_name = u"Food", enabled = True),
            Category(category_name = u"Books", enabled = True),
            Category(category_name = u"Music", enabled = False)
        ]
        for category in self.categories:
            category.insert()

        self.products = [
            Product(
                product_name = u"Cookies",
                price = 5,
                category = self.categories[0]
            ),
            Product(
                product_name = u"Xocolate",
                price = 8,
                category = self.categories[0]
            ),
            Product(
                product_name = u"The Name of the Rose",
                price = 8,
                category = self.categories[1]
            ),
            Product(
                product_name = u"Game of Thrones",
                price = 12,
                category = self.categories[1]
            ),
            Product(
                product_name = u"Paramount",
                price = 15,
                category = self.categories[2]
            ),
            Product(
                product_name = u"Absurditties",
                price = 14,
                category = self.categories[2]
            )
        ]
        for product in self.products:
            product.insert()

        self.orders = [
            Order(product = self.products[0], quantity = 1),
            Order(product = self.products[0], quantity = 2),
            Order(product = self.products[0], quantity = 3),
            Order(product = self.products[2], quantity = 1),
            Order(product = self.products[3], quantity = 2),
            Order(product = self.products[4], quantity = 5),
            Order(product = self.products[5], quantity = 8)
        ]
        for order in self.orders:
            order.insert()

    def test_all(self):

        C = self.Category
        P = self.Product
        O = self.Order

        c = self.categories
        p = self.products
        o = self.orders

        # .all() requires one or more filters
        self.assertRaises(ValueError, P.orders.all)

        # Products where all orders have a quantity greater than 2
        self.assertEqual(
            set(P.select(P.orders.all(O.quantity.greater(2)))),
            set([p[1], p[4], p[5]])
        )

        # Products where all orders have a quantity of 1
        self.assertEqual(
            set(P.select(P.orders.all(quantity = 1))),
            set([p[1], p[2]])
        )

        # Categories where all order quantities exceed 1
        self.assertEqual(
            set(C.select(C.products.all(
                P.orders.none(O.quantity.lower(2))
            ))),
            set([c[2]])
        )
        
    def test_any(self):

        C = self.Category
        P = self.Product
        O = self.Order

        c = self.categories
        p = self.products
        o = self.orders

        # Products with one or more orders
        self.assertEqual(
            set(P.select(P.orders.any())),
            set(x for x in p if x != p[1])
        )

        # Products with one or more orders with quantity > 3
        self.assertEqual(
            set(P.select(P.orders.any(O.quantity.greater(3)))),
            set([p[4], p[5]])
        )

        # Products with orders with quantity = 1
        self.assertEqual(
            set(P.select(P.orders.any(quantity = 1))),
            set([p[0], p[2]])
        )

        # Categories with one or more orders
        self.assertEqual(
            set(C.select(C.products.any(P.orders.any()))),
            set(c)
        )

        # Categories with one or more orders of products with a price greater
        # than 10
        self.assertEqual(
            set(C.select(C.products.any(
                P.price.greater(10),
                P.orders.any()
            ))),
            set([c[1], c[2]])
        )

        # Categories with one or more orders of products with a price greater
        # than 5 and a quantity greater than 4
        self.assertEqual(
            set(C.select(C.products.any(
                P.price.greater(5),
                P.orders.any(O.quantity.greater(4))
            ))),
            set([c[2]])
        )

    def test_none(self):

        C = self.Category
        P = self.Product
        O = self.Order

        c = self.categories
        p = self.products
        o = self.orders

        # Products with no orders
        self.assertEqual(
            set(P.select(P.orders.none())),
            set([p[1]])
        )

        # Products with no orders with a quantity equal to 1
        self.assertEqual(
            set(P.select(P.orders.none(quantity = 1))),
            set([p[1], p[3], p[4], p[5]])
        )

        # Products with no orders with a quantity greater or equal than 3
        self.assertEqual(
            set(P.select(P.orders.none(O.quantity.greater_equal(3)))),
            set([p[1], p[2], p[3]])
        )

        # Categories with no orders
        self.assertEqual(
            set(C.select(C.products.none(P.orders.any()))),
            set()
        )

        # Categories with no orders for products with a price greater or equal
        # than 8
        self.assertEqual(
            set(C.select(C.products.none(
                P.price.greater_equal(8),
                P.orders.any()
            ))),
            set([c[0]])
        )

    def test_has(self):

        C = self.Category
        P = self.Product
        O = self.Order

        c = self.categories
        p = self.products
        o = self.orders

        # Orders of food
        self.assertEqual(
            set(O.select(O.product.has(P.category.equal(c[0])))),
            set([o[0], o[1], o[2]])
        )

        # Orders of books
        self.assertEqual(
            set(O.select(O.product.has(category = c[1]))),
            set([o[3], o[4]])
        )

        # Orders of products of enabled categories
        self.assertEqual(
            set(O.select(
                O.product.has(
                    P.category.has(enabled = True)
                )
            )),
            set([o[0], o[1], o[2], o[3], o[4]])
        )

        # Orders of books with a price greater than 10
        self.assertEqual(
            set(O.select(
                O.product.has(
                    P.price.greater(10),
                    category = c[1]
                )
            )),
            set([o[4]])
        )

