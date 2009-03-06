#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


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

