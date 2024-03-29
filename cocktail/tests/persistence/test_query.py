#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin
from cocktail.translations import set_language


class MemberQueryTestCase(TempStorageMixin, TestCase):

    def assert_queries(self, member, values, *tests):

        from cocktail.persistence import PersistentObject, datastore

        datastore.root.clear()

        if member.schema is None:
            class T(PersistentObject):
                m = member
                i = None

                def __repr__(self):
                    return "%d:%s" % (self.i, self.m.encode("utf-8"))
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

        # Search without duplicates (both on primary and unique fields)
        for primary in (True, False):
            m = String(
                primary = primary,
                unique = True,
                indexed = True,
                required = True
            )

            self.assert_queries(
                m,
                ["foo", "bar", "scrum", "sprunge"],
                (m.equal("zing"), []),
                (m.equal("FOO"), []),
                (m.equal("foo"), [0]),
                (m.equal("scrum"), [2])
            )

        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)

            self.assert_queries(
                m,
                ["foo", "foo", "bar", "scrum", "sprunge", "sprunge"],
                (m.equal("zing"), []),
                (m.equal("FOO"), []),
                (m.equal("foo"), [0, 1]),
                (m.equal("sprunge"), [-2, -1]),
                (m.equal("scrum"), [3])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)

        self.assert_queries(
            m,
            ["foo", "Foo", "Foó"],
            (m.equal("FOO"), [0, 1, 2])
        )

    def test_not_equal(self):

        from cocktail.schema import String

        # Search without duplicates (both on primary and unique fields)
        for primary in (True, False):
            m = String(
                primary = primary,
                unique = True,
                indexed = True,
                required = True
            )

            self.assert_queries(
                m,
                ["foo"],
                (m.not_equal("foo"), [])
            )

        self.assert_queries(
            m,
            ["foo", "bar", "scrum", "sprunge"],
            (m.not_equal("zing"), [0, 1, 2, 3]),
            (m.not_equal("foo"), [1, 2, 3]),
            (m.not_equal("scrum"), [0, 1, 3])
        )

        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)

            self.assert_queries(
                m,
                ["foo", "foo", "bar", "scrum", "sprunge", "sprunge"],
                (m.not_equal("zing"), [0, 1, 2, 3, 4, 5]),
                (m.not_equal("foo"), [2, 3, 4, 5]),
                (m.not_equal("sprunge"), [0, 1, 2, 3]),
                (m.not_equal("scrum"), [0, 1, 2, 4, 5])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)

        self.assert_queries(
            m,
            ["foo", "Foo", "Foó"],
            (m.not_equal("FOO"), []),
            (m.not_equal("bar"), [0, 1, 2])
        )

    def test_greater(self):

        from cocktail.schema import String

        # Search without duplicates (both on primary and unique fields)
        for primary in (True, False):
            m = String(
                primary = primary,
                unique = True,
                indexed = True,
                required = True
            )

            self.assert_queries(
                m,
                ["foo", "bar", "scrum", "SCRUM"],
                (m.greater("zing"), []),
                (m.greater("foo"), [2]),
                (m.greater("A"), [0, 1, 2, 3])
            )

        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)

            self.assert_queries(
                m,
                ["foo", "FOO", "bar", "scrum", "sprunge", "sprunge"],
                (m.greater("zing"), []),
                (m.greater("foo"), [3, 4, 5]),
                (m.greater("scrum"), [4, 5]),
                (m.greater("A"), [0, 1, 2, 3, 4, 5])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)

        self.assert_queries(
            m,
            ["foo", "Foo", "Foó", "bàr", "BaR", "bÄr"],
            (m.greater("A"), [0, 1, 2, 3, 4, 5]),
            (m.greater("a"), [0, 1, 2, 3, 4, 5]),
            (m.greater("f"), [0, 1, 2])
        )

    def test_greater_equal(self):

        from cocktail.schema import String

        # Search without duplicates (both on primary and unique fields)
        for primary in (True, False):
            m = String(
                primary = primary,
                unique = True,
                indexed = True,
                required = True
            )

            self.assert_queries(
                m,
                ["foo", "bar", "scrum", "SCRUM"],
                (m.greater_equal("zing"), []),
                (m.greater_equal("foo"), [0, 2]),
                (m.greater_equal("A"), [0, 1, 2, 3])
            )

        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)

            self.assert_queries(
                m,
                ["foo", "FOO", "bar", "scrum", "sprunge", "sprunge"],
                (m.greater_equal("zing"), []),
                (m.greater_equal("foo"), [0, 3, 4, 5]),
                (m.greater_equal("scrum"), [3, 4, 5]),
                (m.greater_equal("A"), [0, 1, 2, 3, 4, 5])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)

        self.assert_queries(
            m,
            ["foo", "Foo", "Foó", "bàr", "BaR", "bÄr"],
            (m.greater_equal("bar"), [0, 1, 2, 3, 4, 5]),
            (m.greater_equal("BAR"), [0, 1, 2, 3, 4, 5]),
            (m.greater_equal("foo"), [0, 1, 2]),
            (m.greater_equal("FOO"), [0, 1, 2])
        )

    def test_lower(self):

        from cocktail.schema import String

        # Search without duplicates (both on primary and unique fields)
        for primary in (True, False):
            m = String(
                primary = primary,
                unique = True,
                indexed = True,
                required = True
            )

            self.assert_queries(
                m,
                ["foo", "bar", "scrum", "SCRUM"],
                (m.lower("zing"), [0, 1, 2, 3]),
                (m.lower("scrum"), [0, 1, 3]),
                (m.lower("A"), [])
            )

        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)

            self.assert_queries(
                m,
                ["foo", "FOO", "bar", "scrum", "sprunge", "sprunge"],
                (m.lower("zing"), [0, 1, 2, 3, 4, 5]),
                (m.lower("foo"), [1, 2]),
                (m.lower("A"), [])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)

        self.assert_queries(
            m,
            ["foo", "Foo", "Foó", "bàr", "BaR", "bÄr"],
            (m.lower("Z"), [0, 1, 2, 3, 4, 5]),
            (m.lower("z"), [0, 1, 2, 3, 4, 5]),
            (m.lower("f"), [3, 4, 5])
        )

    def test_lower_equal(self):

        from cocktail.schema import String

        # Search without duplicates (both on primary and unique fields)
        for primary in (True, False):
            m = String(
                primary = primary,
                unique = True,
                indexed = True,
                required = True
            )

            self.assert_queries(
                m,
                ["foo", "bar", "scrum", "SCRUM"],
                (m.lower_equal("zing"), [0, 1, 2, 3]),
                (m.lower_equal("foo"), [0, 1, 3]),
                (m.lower_equal("A"), [])
            )

        # Search with duplicates (both with and without an index)
        for indexed in (True, False):
            m = String(indexed = indexed)

            self.assert_queries(
                m,
                ["foo", "FOO", "bar", "scrum", "sprunge", "sprunge"],
                (m.lower_equal("zing"), [0, 1, 2, 3, 4, 5]),
                (m.lower_equal("foo"), [0, 1, 2]),
                (m.lower_equal("A"), [])
            )

        # Normalized string index
        m = String(indexed = True, normalized_index = True)

        self.assert_queries(
            m,
            ["foo", "Foo", "Foó", "bàr", "BaR", "bÄr"],
            (m.lower_equal("bar"), [3, 4, 5]),
            (m.lower_equal("BÀR"), [3, 4, 5]),
            (m.lower_equal("foo"), [0, 1, 2, 3, 4, 5]),
            (m.lower_equal("FOO"), [0, 1, 2, 3, 4, 5])
        )

    def test_range_intersection(self):
        from cocktail.schema import Integer
        from cocktail.schema.expressions import RangeIntersectionExpression
        from cocktail.persistence import PersistentObject

        class Range(PersistentObject):
            a = Integer(indexed = True)
            b = Integer(indexed = True)

        def intersect(a, b, c, d, **kwargs):
            Range.select().delete_items()
            r = Range(a = a, b = b)
            r.insert()
            expr = RangeIntersectionExpression(
                Range.a,
                Range.b,
                c,
                d,
                **kwargs
            )
            q = Range.select([expr])
            order, impl = expr.resolve_filter(q)
            assert impl is not None
            dataset = set([r.id])
            dataset = impl(dataset)
            return list(dataset) == [r.id]

        # Completely apart
        assert not intersect(1, 2, 3, 4)
        assert not intersect(3, 4, 1, 2)
        assert not intersect(None, 1, 2, 3)
        assert not intersect(2, 3, None, 1)
        assert not intersect(1, 2, 3, None)
        assert not intersect(3, None, 1, 2)

        # Single point intersection
        assert intersect(1, 2, 2, 3)
        assert not intersect(3, 4, 2, 3)
        assert not intersect(1, 2, 2, 3, exclude_min = True)
        assert intersect(3, 4, 2, 3, exclude_max = False)

        # Contained
        assert intersect(1, 4, 2, 3)
        assert intersect(2, 3, 1, 4)
        assert intersect(None, None, 1, 2)
        assert intersect(1, 2, None, None)
        assert intersect(None, 3, 1, 2)
        assert intersect(1, 2, None, 3)
        assert intersect(0, None, 1, 2)
        assert intersect(1, 2, 0, None)

        # Equal
        assert not intersect(1, 1, 1, 1)
        assert not intersect(1, 1, 1, 1, exclude_min = True)
        assert intersect(1, 1, 1, 1, exclude_max = False)
        assert not intersect(1, 1, 1, 1, exclude_min = True, exclude_max = False)

        assert intersect(1, 2, 1, 2)
        assert intersect(1, 2, 1, 2, exclude_min = True)
        assert intersect(1, 5, 1, 5, exclude_min = True)
        assert intersect(1, 2, 1, 2, exclude_max = True)
        assert intersect(1, 2, 1, 2, exclude_min = True, exclude_max = True)

        assert intersect(None, None, None, None)
        assert intersect(None, None, None, None, exclude_min = True)
        assert intersect(None, None, None, None, exclude_max = False)
        assert intersect(None, None, None, None,
            exclude_min = True,
            exclude_max = False
        )

        assert intersect(None, 1, None, 1)
        assert intersect(None, 1, None, 1, exclude_min = True)
        assert intersect(None, 1, None, 1, exclude_max = False)
        assert intersect(None, 1, None, 1,
            exclude_min = True,
            exclude_max = False
        )

        assert intersect(1, None, 1, None)
        assert intersect(1, None, 1, None, exclude_min = True)
        assert intersect(1, None, 1, None, exclude_max = False)
        assert intersect(1, None, 1, None,
            exclude_min = True,
            exclude_max = False
        )

        # Partial overlap
        assert intersect(1, 3, 2, 4)
        assert intersect(2, 4, 1, 3)
        assert intersect(None, 5, 3, None)
        assert intersect(3, None, None, 5)


class OrderTestCase(TempStorageMixin, TestCase):

    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail.schema import String, Integer, Boolean
        from cocktail.persistence import PersistentObject

        class Product(PersistentObject):
            product_name = String(
                unique = True,
                indexed = True,
                required = True,
                descriptive = True
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

        a = self.Product.new(product_name = "Wine")
        b = self.Product.new(product_name = "Cheese")
        c = self.Product.new(product_name = "Ham")
        d = self.Product.new(product_name = "Eggs")
        e = self.Product.new()
        f = self.Product.new()

        results = list(self.Product.select(order = "product_name"))
        assert results == [b, d, c, a]

        results = list(self.Product.select(order = "-product_name"))
        assert results == [a, c, d, b]

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
        a.product_name = "Àbac"
        a.insert()

        b = self.Product()
        b.product_name = "alfombra"
        b.insert()

        results = [product
                for product in self.Product.select(order = "product_name")]

        self.assertEqual([a, b], results)

    def test_default_sorting_for_related_objects(self):

        from cocktail.translations import set_language, translations
        from cocktail import schema
        from cocktail.persistence import PersistentObject

        set_language("en")

        class Actor(PersistentObject):

            first_name = schema.String()
            last_name = schema.String()
            movies = schema.Collection(bidirectional = True)

        @translations.instances_of(Actor)
        def translate_actor(self, **kwargs):
            return self.last_name + ", " + self.first_name

        class Movie(PersistentObject):

            title = schema.String()
            lead_actor = schema.Reference(bidirectional = True)

        Actor.movies.items = schema.Reference(type = Movie)
        Movie.lead_actor.type = Actor

        cn = Actor(first_name = "Chuck", last_name = "Norris")
        df2 = Movie(title = "Delta Force 2", lead_actor = cn)
        cn.insert()

        vd = Actor(first_name = "Jean Claude", last_name = "Van Damme")
        us = Movie(title = "Universal Soldier", lead_actor = vd)
        vd.insert()

        cb = Actor(first_name = "Charles", last_name = "Bronson")
        dw = Movie(title = "Death Wish", lead_actor = cb)
        cb.insert()

        ss = Actor(first_name = "Steven", last_name = "Seagal")
        htk = Movie(title = "Hard to Kill", lead_actor = ss)
        ss.insert()

        sorted_movies = list(Movie.select(order = Movie.lead_actor))
        assert sorted_movies == [dw, df2, htk, us]

    def test_custom_sorting_for_related_objects(self):

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class Review(PersistentObject):
            points = schema.Integer()
            project = schema.Reference(bidirectional = True)

            def get_ordering_key(self):
                return self.points

        class Project(PersistentObject):
            title = schema.String()
            review = schema.Reference(bidirectional = True)

        Review.project.type = Project
        Project.review.type = Review

        p1 = Project(title = 'Project 1')
        r1 = Review(points = 2, project = p1)
        p1.insert()

        p2 = Project(title = 'Project 2')
        r2 = Review(points = 11, project = p2)
        p2.insert()

        p3 = Project(title = 'Project 3')
        r3 = Review(points = 1, project = p3)
        p3.insert()

        sorted_projects = list(Project.select(order = Project.review))
        assert sorted_projects == [p3, p1, p2]

class TranslatedOrderTestCase(TempStorageMixin, TestCase):

    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail.schema import String, Integer
        from cocktail.persistence import PersistentObject

        class Product(PersistentObject):
            product_name = String(
                unique = True,
                indexed = True,
                required = True,
                translated = True
            )
            category = String(
                indexed = True,
                translated = True
            )
            subcategory = String(
                indexed = True,
                translated = True
            )
            color = String(
                translated = True
            )
            country = String(
                translated = True
            )
            price = Integer(
                indexed = True
            )
            weight = Integer()

        self.Product = Product

    def match(self, results, *group):
        results_group = set(results.pop(0) for i in range(len(group)))
        self.assertEqual(results_group, set(group))

    def test_single_indexed_unique_translated_member(self):

        a = self.Product()
        a.set("product_name", "Poma", "ca")
        a.set("product_name", "Apple", "en")
        a.insert()

        b = self.Product()
        b.set("product_name", "Formatge", "ca")
        b.set("product_name", "Cheese", "en")
        b.insert()

        c = self.Product()
        c.set("product_name", "Pernil", "ca")
        c.set("product_name", "Ham", "en")
        c.insert()

        d = self.Product()
        d.set("product_name", "Ous", "ca")
        d.set("product_name", "Eggs", "en")
        d.insert()

        e = self.Product()
        e.set("product_name", "Suc", "ca")
        e.set("product_name", "Juice", "en")
        e.insert()

        set_language("ca")

        results = [product
                   for product in self.Product.select(order = "product_name")]
        assert [b, d, c, a, e] == results

        results = [product
                   for product in self.Product.select(order = "-product_name")]
        assert [e, a, c, d, b] == results

        set_language("en")

        results = [product
                   for product in self.Product.select(order = "product_name")]
        assert [a, b, d, c, e] == results

        results = [product
                   for product in self.Product.select(order = "-product_name")]
        assert [e, c, d, b, a] == results

    def test_single_not_indexed_translated_member(self):

        a = self.Product()
        a.set("color", "vermell", "ca")
        a.set("color", "red", "en")
        a.insert()

        b = self.Product()
        b.set("color", "verd", "ca")
        b.set("color", "green", "en")
        b.insert()

        c = self.Product()
        c.set("color", "blau", "ca")
        c.set("color", "blue", "en")
        c.insert()

        d = self.Product()
        d.set("color", "verd", "ca")
        d.set("color", "green", "en")
        d.insert()

        e = self.Product()
        e.set("color", "vermell", "ca")
        e.set("color", "red", "en")
        e.insert()

        f = self.Product()
        f.set("color", "blau", "ca")
        f.set("color", "blue", "en")
        f.insert()

        set_language("ca")

        results = [product for product in self.Product.select(order = "color")]
        self.match(results, c, f)
        self.match(results, b, d)
        self.match(results, a, e)

        results = [product
                   for product in self.Product.select(order = "-color")]
        self.match(results, a, e)
        self.match(results, b, d)
        self.match(results, c, f)

        set_language("en")

        results = [product for product in self.Product.select(order = "color")]
        self.match(results, c, f)
        self.match(results, b, d)
        self.match(results, a, e)

        results = [product
                   for product in self.Product.select(order = "-color")]
        self.match(results, a, e)
        self.match(results, b, d)
        self.match(results, c, f)

    def test_not_indexed_not_translated_vs_not_indexed_translated(self):

        a = self.Product()
        a.weight = 3
        a.set("color", "vermell", "ca")
        a.set("color", "red", "en")
        a.insert()

        b = self.Product()
        b.weight = 4
        b.set("color", "verd", "ca")
        b.set("color", "green", "en")
        b.insert()

        c = self.Product()
        c.weight = 4
        c.set("color", "groc", "ca")
        c.set("color", "yellow", "en")
        c.insert()

        d = self.Product()
        d.weight = 3
        d.set("color", "verd", "ca")
        d.set("color", "green", "en")
        d.insert()

        e = self.Product()
        e.weight = 1
        e.set("color", "groc", "ca")
        e.set("color", "yellow", "en")
        e.insert()

        f = self.Product()
        f.weight = 7
        f.set("color", "vermell", "ca")
        f.set("color", "red", "en")
        f.insert()

        set_language("ca")

        results = [product
                   for product in self.Product.select(
                       order = ("weight", "color"))]

        assert [e, d, a, c, b, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("weight", "-color"))]

        assert [e, a, d, b, c, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-weight", "color"))]

        assert [f, c, b, d, a, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-weight", "-color"))]

        assert [f, b, c, a, d, e] == results

        set_language("en")

        results = [product
                   for product in self.Product.select(
                       order = ("weight", "color"))]

        assert [e, d, a, b, c, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("weight", "-color"))]

        assert [e, a, d, c, b, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-weight", "color"))]

        assert [f, b, c, d, a, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-weight", "-color"))]

        assert [f, c, b, a, d, e] == results

    def test_not_indexed_not_translated_vs_indexed_translated(self):

        a = self.Product()
        a.weight = 3
        a.set("category", "esports", "ca")
        a.set("category", "sports", "en")
        a.insert()

        b = self.Product()
        b.weight = 4
        b.set("category", "fotografia", "ca")
        b.set("category", "photography", "en")
        b.insert()

        c = self.Product()
        c.weight = 4
        c.set("category", "menjar", "ca")
        c.set("category", "food", "en")
        c.insert()

        d = self.Product()
        d.weight = 3
        d.set("category", "fotografia", "ca")
        d.set("category", "photography", "en")
        d.insert()

        e = self.Product()
        e.weight = 1
        e.set("category", "menjar", "ca")
        e.set("category", "food", "en")
        e.insert()

        f = self.Product()
        f.weight = 7
        f.set("category", "esports", "ca")
        f.set("category", "sports", "en")
        f.insert()

        set_language("ca")

        results = [product
                   for product in self.Product.select(
                       order = ("weight", "category"))]

        assert [e, a, d, b, c, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("weight", "-category"))]

        assert [e, d, a, c, b, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-weight", "category"))]

        assert [f, b, c, a, d, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-weight", "-category"))]

        assert [f, c, b, d, a, e] == results

        set_language("en")

        results = [product
                   for product in self.Product.select(
                       order = ("weight", "category"))]

        assert [e, d, a, c, b, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("weight", "-category"))]

        assert [e, a, d, b, c, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-weight", "category"))]

        assert [f, c, b, d, a, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-weight", "-category"))]

        assert [f, b, c, a, d, e] == results

    def test_indexed_not_translated_vs_not_indexed_translated(self):

        a = self.Product()
        a.price = 3
        a.set("color", "vermell", "ca")
        a.set("color", "red", "en")
        a.insert()

        b = self.Product()
        b.price = 4
        b.set("color", "verd", "ca")
        b.set("color", "green", "en")
        b.insert()

        c = self.Product()
        c.price = 4
        c.set("color", "groc", "ca")
        c.set("color", "yellow", "en")
        c.insert()

        d = self.Product()
        d.price = 3
        d.set("color", "verd", "ca")
        d.set("color", "green", "en")
        d.insert()

        e = self.Product()
        e.price = 1
        e.set("color", "groc", "ca")
        e.set("color", "yellow", "en")
        e.insert()

        f = self.Product()
        f.price = 7
        f.set("color", "vermell", "ca")
        f.set("color", "red", "en")
        f.insert()

        set_language("ca")

        results = [product
                   for product in self.Product.select(
                       order = ("price", "color"))]

        assert [e, d, a, c, b, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("price", "-color"))]

        assert [e, a, d, b, c, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-price", "color"))]

        assert [f, c, b, d, a, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-price", "-color"))]

        assert [f, b, c, a, d, e] == results

        set_language("en")

        results = [product
                   for product in self.Product.select(
                       order = ("price", "color"))]

        assert [e, d, a, b, c, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("price", "-color"))]

        assert [e, a, d, c, b, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-price", "color"))]

        assert [f, b, c, d, a, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-price", "-color"))]

        assert [f, c, b, a, d, e] == results

    def test_indexed_not_translated_vs_indexed_translated(self):

        a = self.Product()
        a.price = 3
        a.set("category", "esports", "ca")
        a.set("category", "sports", "en")
        a.insert()

        b = self.Product()
        b.price = 4
        b.set("category", "fotografia", "ca")
        b.set("category", "photography", "en")
        b.insert()

        c = self.Product()
        c.price = 4
        c.set("category", "menjar", "ca")
        c.set("category", "food", "en")
        c.insert()

        d = self.Product()
        d.price = 3
        d.set("category", "fotografia", "ca")
        d.set("category", "photography", "en")
        d.insert()

        e = self.Product()
        e.price = 1
        e.set("category", "menjar", "ca")
        e.set("category", "food", "en")
        e.insert()

        f = self.Product()
        f.price = 7
        f.set("category", "esports", "ca")
        f.set("category", "sports", "en")
        f.insert()

        set_language("ca")

        results = [product
                   for product in self.Product.select(
                       order = ("price", "category"))]

        assert [e, a, d, b, c, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("price", "-category"))]

        assert [e, d, a, c, b, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-price", "category"))]

        assert [f, b, c, a, d, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-price", "-category"))]

        assert [f, c, b, d, a, e] == results

        set_language("en")

        results = [product
                   for product in self.Product.select(
                       order = ("price", "category"))]

        assert [e, d, a, c, b, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("price", "-category"))]

        assert [e, a, d, b, c, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-price", "category"))]

        assert [f, c, b, d, a, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-price", "-category"))]

        assert [f, b, c, a, d, e] == results

    def test_not_indexed_translated_vs_not_indexed_translated(self):

        a = self.Product()
        a.set("color", "vermell", "ca")
        a.set("color", "red", "en")
        a.set("country", "espanya", "ca")
        a.set("country", "spain", "en")
        a.insert()

        b = self.Product()
        b.set("color", "verd", "ca")
        b.set("color", "green", "en")
        b.set("country", "espanya", "ca")
        b.set("country", "spain", "en")
        b.insert()

        c = self.Product()
        c.set("color", "groc", "ca")
        c.set("color", "yellow", "en")
        c.set("country", "anglaterra", "ca")
        c.set("country", "england", "en")
        c.insert()

        d = self.Product()
        d.set("color", "verd", "ca")
        d.set("color", "green", "en")
        d.set("country", "estats units", "ca")
        d.set("country", "united states", "en")
        d.insert()

        e = self.Product()
        e.set("color", "groc", "ca")
        e.set("color", "yellow", "en")
        e.set("country", "estats units", "ca")
        e.set("country", "united states", "en")
        e.insert()

        f = self.Product()
        f.set("color", "vermell", "ca")
        f.set("color", "red", "en")
        f.set("country", "anglaterra", "ca")
        f.set("country", "england", "en")
        f.insert()

        set_language("ca")

        results = [product
                   for product in self.Product.select(
                       order = ("color", "country"))]

        assert [c, e, b, d, f, a] == results

        results = [product
                   for product in self.Product.select(
                       order = ("color", "-country"))]

        assert [e, c, d, b, a, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-color", "country"))]

        assert [f, a, b, d, c, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-color", "-country"))]

        assert [a, f, d, b, e, c] == results

        set_language("en")

        results = [product
                   for product in self.Product.select(
                       order = ("color", "country"))]

        assert [b, d, f, a, c, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("color", "-country"))]

        assert [d, b, a, f, e, c] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-color", "country"))]

        assert [c, e, f, a, b, d] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-color", "-country"))]

        assert [e, c, a, f, d, b] == results

    def test_not_indexed_translated_vs_indexed_translated(self):

        a = self.Product()
        a.set("color", "vermell", "ca")
        a.set("color", "red", "en")
        a.set("category", "esports", "ca")
        a.set("category", "sports", "en")
        a.insert()

        b = self.Product()
        b.set("color", "verd", "ca")
        b.set("color", "green", "en")
        b.set("category", "menjar", "ca")
        b.set("category", "food", "en")
        b.insert()

        c = self.Product()
        c.set("color", "groc", "ca")
        c.set("color", "yellow", "en")
        c.set("category", "menjar", "ca")
        c.set("category", "food", "en")
        c.insert()

        d = self.Product()
        d.set("color", "verd", "ca")
        d.set("color", "green", "en")
        d.set("category", "fotografia", "ca")
        d.set("category", "photography", "en")
        d.insert()

        e = self.Product()
        e.set("color", "groc", "ca")
        e.set("color", "yellow", "en")
        e.set("category", "esports", "ca")
        e.set("category", "sports", "en")
        e.insert()

        f = self.Product()
        f.set("color", "vermell", "ca")
        f.set("color", "red", "en")
        f.set("category", "fotografia", "ca")
        f.set("category", "photography", "en")
        f.insert()

        set_language("ca")

        results = [product
                   for product in self.Product.select(
                       order = ("color", "category"))]

        assert [e, c, d, b, a, f] == results

        results = [product
                   for product in self.Product.select(
                       order = ("color", "-category"))]

        assert [c, e, b, d, f, a] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-color", "category"))]

        assert [a, f, d, b, e, c] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-color", "-category"))]

        assert [f, a, b, d, c, e] == results

        set_language("en")

        results = [product
                   for product in self.Product.select(
                       order = ("color", "category"))]

        assert [b, d, f, a, c, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("color", "-category"))]

        assert [d, b, a, f, e, c] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-color", "category"))]

        assert [c, e, f, a, b, d] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-color", "-category"))]

        assert [e, c, a, f, d, b] == results

    def test_indexed_translated_vs_indexed_translated(self):

        a = self.Product()
        a.set("category", "esports", "ca")
        a.set("category", "sports", "en")
        a.set("subcategory", "futbol", "ca")
        a.set("subcategory", "soccer", "en")
        a.insert()

        b = self.Product()
        b.set("category", "menjar", "ca")
        b.set("category", "food", "en")
        b.set("subcategory", "peix", "ca")
        b.set("subcategory", "fish", "en")
        b.insert()

        c = self.Product()
        c.set("category", "menjar", "ca")
        c.set("category", "food", "en")
        c.set("subcategory", "carn", "ca")
        c.set("subcategory", "meat", "en")
        c.insert()

        d = self.Product()
        d.set("category", "fotografia", "ca")
        d.set("category", "photography", "en")
        d.set("subcategory", "paisatge", "ca")
        d.set("subcategory", "landscape", "en")
        d.insert()

        e = self.Product()
        e.set("category", "esports", "ca")
        e.set("category", "sports", "en")
        e.set("subcategory", "esqui", "ca")
        e.set("subcategory", "ski", "en")
        e.insert()

        f = self.Product()
        f.set("category", "fotografia", "ca")
        f.set("category", "photography", "en")
        f.set("subcategory", "retrat", "ca")
        f.set("subcategory", "portrait", "en")
        f.insert()

        set_language("ca")

        results = [product
                   for product in self.Product.select(
                       order = ("category", "subcategory"))]

        assert [e, a, d, f, c, b] == results

        results = [product
                   for product in self.Product.select(
                       order = ("category", "-subcategory"))]

        assert [a, e, f, d, b, c] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-category", "subcategory"))]

        assert [c, b, d, f, e, a] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-category", "-subcategory"))]

        assert [b, c, f, d, a, e] == results

        set_language("en")

        results = [product
                   for product in self.Product.select(
                       order = ("category", "subcategory"))]

        assert [b, c, d, f, e, a] == results

        results = [product
                   for product in self.Product.select(
                       order = ("category", "-subcategory"))]

        assert [c, b, f, d, a, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-category", "subcategory"))]

        assert [e, a, d, f, b, c] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-category", "-subcategory"))]

        assert [a, e, f, d, c, b] == results

    def test_indexed_translated_vs_indexed_unique_translated(self):

        a = self.Product()
        a.set("category", "esports", "ca")
        a.set("category", "sports", "en")
        a.set("product_name", "Poma", "ca")
        a.set("product_name", "Apple", "en")
        a.insert()

        b = self.Product()
        b.set("category", "menjar", "ca")
        b.set("category", "food", "en")
        b.set("product_name", "Formatge", "ca")
        b.set("product_name", "Cheese", "en")
        b.insert()

        c = self.Product()
        c.set("category", "menjar", "ca")
        c.set("category", "food", "en")
        c.set("product_name", "Pernil", "ca")
        c.set("product_name", "Ham", "en")
        c.insert()

        d = self.Product()
        d.set("category", "fotografia", "ca")
        d.set("category", "photography", "en")
        d.set("product_name", "Ous", "ca")
        d.set("product_name", "Eggs", "en")
        d.insert()

        e = self.Product()
        e.set("category", "esports", "ca")
        e.set("category", "sports", "en")
        e.set("product_name", "Suc", "ca")
        e.set("product_name", "Juice", "en")
        e.insert()

        f = self.Product()
        f.set("category", "fotografia", "ca")
        f.set("category", "photography", "en")
        f.set("product_name", "Carret", "ca")
        f.set("product_name", "Roll", "en")
        f.insert()

        set_language("ca")

        results = [product
                   for product in self.Product.select(
                       order = ("category", "product_name"))]

        assert [a, e, f, d, b, c] == results

        results = [product
                   for product in self.Product.select(
                       order = ("category", "-product_name"))]

        assert [e, a, d, f, c, b] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-category", "product_name"))]

        assert [b, c, f, d, a, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-category", "-product_name"))]

        assert [c, b, d, f, e, a] == results

        set_language("en")

        results = [product
                   for product in self.Product.select(
                       order = ("category", "product_name"))]

        assert [b, c, d, f, a, e] == results

        results = [product
                   for product in self.Product.select(
                       order = ("category", "-product_name"))]

        assert [c, b, f, d, e, a] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-category", "product_name"))]

        assert [a, e, d, f, b, c] == results

        results = [product
                   for product in self.Product.select(
                       order = ("-category", "-product_name"))]

        assert [e, a, f, d, c, b] == results


class StringCollectionQueriesTestCase(TempStorageMixin, TestCase):

    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class TestObject(PersistentObject):

            test_collection = schema.Collection(
                items = schema.String(),
                indexed = True
            )

        self.TestObject = TestObject

    def test_can_select_collections_containing_an_item(self):

        T = self.TestObject

        a = T()
        a.test_collection.append("foo")
        a.test_collection.append("bar")
        a.test_collection.append("spam")
        a.insert()

        b = T()
        b.test_collection.append("foo")
        b.test_collection.append("bar")
        b.insert()

        c = T()
        c.test_collection.append("foo")
        c.insert()

        assert set(T.select(T.test_collection.contains("foo"))) == set([a, b, c])
        assert set(T.select(T.test_collection.contains("bar"))) == set([a, b])
        assert set(T.select(T.test_collection.contains("spam"))) == set([a])
        assert set(T.select(T.test_collection.contains("scrum"))) == set()

    def test_can_select_collections_containing_one_or_more_items_from_a_subset(self):

        T = self.TestObject

        a = T()
        a.test_collection.append("a")
        a.test_collection.append("x")
        a.insert()

        b = T()
        b.test_collection.append("b")
        b.test_collection.append("x")
        b.insert()

        c = T()
        c.test_collection.append("c")
        c.test_collection.append("y")
        c.insert()

        assert set(T.select(T.test_collection.contains_any(["x", "y"]))) == set([a, b, c])
        assert set(T.select(T.test_collection.contains_any(["a"]))) == set([a])
        assert set(T.select(T.test_collection.contains_any(["b", "c"]))) == set([b, c])
        assert set(T.select(T.test_collection.contains_any(["N", "M"]))) == set()

    def test_can_select_collections_containing_all_items_from_a_subset(self):

        T = self.TestObject

        a = T()
        a.test_collection.append("a")
        a.test_collection.append("x")
        a.test_collection.append("y")
        a.insert()

        b = T()
        b.test_collection.append("b")
        b.test_collection.append("x")
        b.test_collection.append("y")
        b.insert()

        c = T()
        c.test_collection.append("c")
        c.test_collection.append("y")
        c.insert()

        assert set(T.select(T.test_collection.contains_all(["x", "y"]))) == set([a, b])
        assert set(T.select(T.test_collection.contains_all(["a", "x", "y"]))) == set([a])
        assert set(T.select(T.test_collection.contains_all(["y"]))) == set([a, b, c])
        assert set(T.select(T.test_collection.contains_all(["x", "Z"]))) == set()

    def test_can_select_collections_lacking_an_item(self):

        T = self.TestObject

        a = T()
        a.test_collection.append("foo")
        a.test_collection.append("bar")
        a.test_collection.append("spam")
        a.insert()

        b = T()
        b.test_collection.append("foo")
        b.test_collection.append("bar")
        b.insert()

        c = T()
        c.test_collection.append("foo")
        c.insert()

        assert set(T.select(T.test_collection.lacks("foo"))) == set()
        assert set(T.select(T.test_collection.lacks("bar"))) == set([c])
        assert set(T.select(T.test_collection.lacks("spam"))) == set([b, c])
        assert set(T.select(T.test_collection.lacks("scrum"))) == set([a, b, c])


class ReferenceCollectionQueriesTestCase(TempStorageMixin, TestCase):

    def setUp(self):

        TempStorageMixin.setUp(self)

        from cocktail import schema
        from cocktail.persistence import PersistentObject

        class Document(PersistentObject):
            pass

        class Tag(PersistentObject):

            documents = schema.Collection(
                items = schema.Reference(type = Document),
                related_end = schema.Collection("tags",
                    indexed = True
                ),
                indexed = True
            )

        self.Document = Document
        self.Tag = Tag

    def test_can_select_collections_containing_an_item(self):

        Doc = self.Document
        Tag = self.Tag

        d1 = Doc(); d1.insert()
        d2 = Doc(); d2.insert()
        d3 = Doc(); d3.insert()
        d4 = Doc(); d4.insert()

        t1 = Tag(); t1.insert()
        t2 = Tag(); t2.insert()
        t3 = Tag(); t3.insert()
        t4 = Tag(); t4.insert()

        d1.tags = [t1, t2]
        d2.tags = [t2, t3]
        d3.tags = [t2, t3]

        assert set(Doc.select(Doc.tags.contains(t1))) == set([d1])
        assert set(Doc.select(Doc.tags.contains(t2))) == set([d1, d2, d3])
        assert set(Doc.select(Doc.tags.contains(t3))) == set([d2, d3])
        assert set(Doc.select(Doc.tags.contains(t4))) == set()

    def test_can_select_collections_containing_one_or_more_items_from_a_subset(self):

        Doc = self.Document
        Tag = self.Tag

        d1 = Doc(); d1.insert()
        d2 = Doc(); d2.insert()
        d3 = Doc(); d3.insert()
        d4 = Doc(); d4.insert()

        t1 = Tag(); t1.insert()
        t2 = Tag(); t2.insert()
        t3 = Tag(); t3.insert()
        t4 = Tag(); t4.insert()
        t5 = Tag(); t5.insert()
        t6 = Tag(); t6.insert()

        d1.tags = [t1, t2]
        d2.tags = [t1, t3]
        d3.tags = [t4]

        assert set(Doc.select(Doc.tags.contains_any([t3, t4]))) == set([d2, d3])
        assert set(Doc.select(Doc.tags.contains_any([t1, t4]))) == set([d1, d2, d3])
        assert set(Doc.select(Doc.tags.contains_any([t2, t5]))) == set([d1])
        assert set(Doc.select(Doc.tags.contains_any([t5, t6]))) == set()

    def test_can_select_collections_containing_all_items_from_a_subset(self):

        Doc = self.Document
        Tag = self.Tag

        d1 = Doc(); d1.insert()
        d2 = Doc(); d2.insert()
        d3 = Doc(); d3.insert()
        d4 = Doc(); d4.insert()

        t1 = Tag(); t1.insert()
        t2 = Tag(); t2.insert()
        t3 = Tag(); t3.insert()
        t4 = Tag(); t4.insert()
        t5 = Tag(); t5.insert()
        t6 = Tag(); t6.insert()

        d1.tags = [t1, t2, t5]
        d2.tags = [t1, t3, t5]
        d3.tags = [t2]

        assert set(Doc.select(Doc.tags.contains_all([t1, t5]))) == set([d1, d2])
        assert set(Doc.select(Doc.tags.contains_all([t1]))) == set([d1, d2])
        assert set(Doc.select(Doc.tags.contains_all([t2, t5]))) == set([d1])
        assert set(Doc.select(Doc.tags.contains_all([t4]))) == set()
        assert set(Doc.select(Doc.tags.contains_all([t4, t1]))) == set()

    def test_can_select_collections_lacking_an_item(self):

        Doc = self.Document
        Tag = self.Tag

        d1 = Doc(); d1.insert()
        d2 = Doc(); d2.insert()
        d3 = Doc(); d3.insert()
        d4 = Doc(); d4.insert()

        t1 = Tag(); t1.insert()
        t2 = Tag(); t2.insert()
        t3 = Tag(); t3.insert()
        t4 = Tag(); t4.insert()
        t5 = Tag(); t5.insert()
        t6 = Tag(); t6.insert()

        d1.tags = [t1, t2, t5]
        d2.tags = [t1, t3, t5]
        d3.tags = [t2]

        assert set(Doc.select(Doc.tags.lacks(t1))) == set([d3, d4])
        assert set(Doc.select(Doc.tags.lacks(t2))) == set([d2, d4])
        assert set(Doc.select(Doc.tags.lacks(t3))) == set([d1, d3, d4])
        assert set(Doc.select(Doc.tags.lacks(t4))) == set([d1, d2, d3, d4])
        assert set(Doc.select(Doc.tags.lacks(t5))) == set([d3, d4])
        assert set(Doc.select(Doc.tags.lacks(t6))) == set([d1, d2, d3, d4])


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
                return self.product_name or PersistentObject.__repr__(self)

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
            Category(category_name = "Food", enabled = True),
            Category(category_name = "Books", enabled = True),
            Category(category_name = "Music", enabled = False)
        ]
        for category in self.categories:
            category.insert()

        self.products = [
            Product(
                product_name = "Cookies",
                price = 5,
                category = self.categories[0]
            ),
            Product(
                product_name = "Xocolate",
                price = 8,
                category = self.categories[0]
            ),
            Product(
                product_name = "The Name of the Rose",
                price = 8,
                category = self.categories[1]
            ),
            Product(
                product_name = "Game of Thrones",
                price = 12,
                category = self.categories[1]
            ),
            Product(
                product_name = "Paramount",
                price = 15,
                category = self.categories[2]
            ),
            Product(
                product_name = "Absurditties",
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

    def test_isinstance(self):

        from cocktail.persistence import PersistentObject, datastore
        from cocktail.schema.expressions import Self, IsInstanceExpression

        datastore.root.clear()

        class Category(PersistentObject):
            pass

        class C1(Category):
            pass

        class C2(Category):
            pass

        a = C1()
        a.insert()

        b = C1()
        b.insert()

        c = C2()
        c.insert()

        d = C2()
        d.insert()

        assert set(Category.select(Self.isinstance(C1))) == \
            set([a, b])
        assert not set(Category.select(Self.isinstance(C1))) == \
            set([c, d])
        assert set(Category.select(Self.isinstance(C2))) == \
            set([c, d])
        assert not set(Category.select(Self.isinstance(C2))) == \
            set([a, b])
        assert set(Category.select(Self.isinstance((C1, C2)))) == \
            set([a, b, c, d])
        assert set(Category.select(Self.isinstance(Category))) == \
            set([a, b, c, d])
        assert set(Category.select(
            IsInstanceExpression(Self, Category, is_inherited = False)
        )) == set()

    def test_is_not_instance(self):

        from cocktail.persistence import PersistentObject, datastore
        from cocktail.schema.expressions import Self, IsNotInstanceExpression

        datastore.root.clear()

        class Category(PersistentObject):
            pass

        class C1(Category):
            pass

        class C2(Category):
            pass

        a = C1()
        a.insert()

        b = C1()
        b.insert()

        c = C2()
        c.insert()

        d = C2()
        d.insert()

        assert not set(Category.select(Self.is_not_instance(C1))) == \
            set([a, b])
        assert set(Category.select(Self.is_not_instance(C1))) == \
            set([c, d])
        assert not set(Category.select(Self.is_not_instance(C2))) == \
            set([c, d])
        assert set(Category.select(Self.is_not_instance(C2))) == \
            set([a, b])
        assert set(Category.select(Self.is_not_instance((C1, C2)))) == \
            set()
        assert set(Category.select(Self.is_not_instance(Category))) == \
            set()
        assert set(Category.select(
            IsNotInstanceExpression(Self, Category,is_inherited = False))
        ) == set([a, b, c, d])


class DescendsFromTestCase(TempStorageMixin, TestCase):

    def setUp(self):
        TempStorageMixin.setUp(self)

        from cocktail.schema import Reference, Collection
        from cocktail.persistence import PersistentObject, datastore

        datastore.root.clear()

        class Document(PersistentObject):
            parent = Reference(
                bidirectional = True,
                related_key = "children"
            )
            children = Collection(
                bidirectional = True,
                related_key = "parent"
            )

            extension = Reference(
                bidirectional = True,
                related_key = "extended"
            )
            extended = Reference(
                bidirectional = True,
                related_key = "extension"
            )

            improvement = Reference()
            related_documents = Collection()

        Document.extension.type = Document
        Document.extended.type = Document
        Document.parent.type = Document
        Document.children.items = Reference(type = Document)
        Document.improvement.type = Document
        Document.related_documents.items = Reference(type = Document)

        self.Document = Document

    def test_descends_from_one_to_one_bidirectional(self):
        from cocktail.schema.expressions import DescendsFromExpression, Self

        a = self.Document()
        b = self.Document()
        c = self.Document()

        a.extension = b
        b.extension = c

        a.insert()
        b.insert()
        c.insert()

        assert set(self.Document.select(
            Self.descends_from(a, self.Document.extension)
        )) == set([a, b, c])
        assert set(self.Document.select(
            Self.descends_from(a, self.Document.extension, include_self = False)
        )) == set([b, c])
        assert set(self.Document.select(
            Self.descends_from(b, self.Document.extension)
        )) == set([b, c])
        assert set(self.Document.select(
            Self.descends_from(b, self.Document.extension, include_self = False)
        )) == set([c])
        assert set(self.Document.select(
            Self.descends_from(c, self.Document.extension)
        )) == set([c])
        assert set(self.Document.select(
            Self.descends_from(c, self.Document.extension, include_self = False)
        )) == set([])

    def test_descends_from_one_to_many_bidirectional(self):
        from cocktail.schema.expressions import DescendsFromExpression, Self

        a = self.Document()
        b = self.Document()
        c = self.Document()
        d = self.Document()
        e = self.Document()

        a.children = [b, c]
        b.children = [d, e]

        a.insert()
        b.insert()
        c.insert()
        d.insert()
        e.insert()

        assert set(self.Document.select(
            Self.descends_from(a, self.Document.children)
        )) == set([a, b, c, d, e])
        assert set(self.Document.select(
            Self.descends_from(a, self.Document.children, include_self = False)
        )) == set([b, c, d, e])
        assert set(self.Document.select(
            Self.descends_from(b, self.Document.children)
        )) == set([b, d, e])
        assert set(self.Document.select(
            Self.descends_from(b, self.Document.children, include_self = False)
        )) == set([d, e])
        assert set(self.Document.select(
            Self.descends_from(c, self.Document.children)
        )) == set([c])
        assert set(self.Document.select(
            Self.descends_from(c, self.Document.children, include_self = False)
        )) == set([])
        assert set(self.Document.select(
            Self.descends_from(d, self.Document.children)
        )) == set([d])
        assert set(self.Document.select(
            Self.descends_from(d, self.Document.children, include_self = False)
        )) == set([])

    def test_descends_from_one_to_one(self):
        from cocktail.schema.expressions import DescendsFromExpression, Self

        a = self.Document()
        b = self.Document()
        c = self.Document()

        a.improvement = b
        b.improvement = c

        a.insert()
        b.insert()
        c.insert()

        assert set(self.Document.select(
            Self.descends_from(a, self.Document.improvement)
        )) == set([a, b, c])
        assert set(self.Document.select(
            Self.descends_from(
                a, self.Document.improvement, include_self = False
            )
        )) == set([b, c])
        assert set(self.Document.select(
            Self.descends_from(
                b, self.Document.improvement, include_self = False
            )
        )) == set([c])
        assert set(self.Document.select(
            Self.descends_from(c, self.Document.improvement)
        )) == set([c])
        assert set(self.Document.select(
            Self.descends_from(
                c, self.Document.improvement, include_self = False
            )
        )) == set([])

    def test_descends_from_many_to_many(self):
        from cocktail.schema.expressions import DescendsFromExpression, Self

        a = self.Document()
        b = self.Document()
        c = self.Document()
        d = self.Document()
        e = self.Document()

        a.related_documents = [b, c]
        b.related_documents = [d, e]

        a.insert()
        b.insert()
        c.insert()
        d.insert()
        e.insert()

        assert set(self.Document.select(
            Self.descends_from(a, self.Document.related_documents)
        )) == set([a, b, c, d, e])
        assert set(self.Document.select(
            Self.descends_from(
                a, self.Document.related_documents, include_self = False
            )
        )) == set([b, c, d, e])
        assert set(self.Document.select(
            Self.descends_from(b, self.Document.related_documents)
        )) == set([b, d, e])
        assert set(self.Document.select(
            Self.descends_from(
                b, self.Document.related_documents, include_self = False
            )
        )) == set([d, e])
        assert set(self.Document.select(
            Self.descends_from(c, self.Document.related_documents)
        )) == set([c])
        assert set(self.Document.select(
            Self.descends_from(
                c, self.Document.related_documents, include_self = False
            )
        )) == set([])
        assert set(self.Document.select(
            Self.descends_from(d, self.Document.related_documents)
        )) == set([d])
        assert set(self.Document.select(
            Self.descends_from(
                d, self.Document.related_documents, include_self = False
            )
        )) == set([])

