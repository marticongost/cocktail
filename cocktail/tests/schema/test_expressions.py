#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class ComparisonTestCase(TempStorageMixin, TestCase):

    def test_eval_greater(self):
        from cocktail.schema.expressions import GreaterExpression
        assert GreaterExpression(3, 2).eval({})
        assert not GreaterExpression(2, 2).eval({})
        assert not GreaterExpression(1, 2).eval({})
        assert GreaterExpression(1, None).eval({})
        assert not GreaterExpression(None, None).eval({})
        assert not GreaterExpression(None, 3).eval({})

    def test_eval_greater_equal(self):
        from cocktail.schema.expressions import GreaterEqualExpression
        assert GreaterEqualExpression(3, 2).eval({})
        assert GreaterEqualExpression(2, 2).eval({})
        assert not GreaterEqualExpression(1, 2).eval({})
        assert GreaterEqualExpression(1, None).eval({})
        assert GreaterEqualExpression(None, None).eval({})
        assert not GreaterEqualExpression(None, 3).eval({})

    def test_eval_lower(self):
        from cocktail.schema.expressions import LowerExpression
        assert not LowerExpression(3, 2).eval({})
        assert not LowerExpression(2, 2).eval({})
        assert LowerExpression(1, 2).eval({})
        assert not LowerExpression(1, None).eval({})
        assert not LowerExpression(None, None).eval({})
        assert LowerExpression(None, 3).eval({})

    def test_eval_lower_equal(self):
        from cocktail.schema.expressions import LowerEqualExpression        
        assert not LowerEqualExpression(3, 2).eval({})
        assert LowerEqualExpression(2, 2).eval({})
        assert LowerEqualExpression(1, 2).eval({})
        assert not LowerEqualExpression(1, None).eval({})
        assert LowerEqualExpression(None, None).eval({})
        assert LowerEqualExpression(None, 3).eval({})

    def test_eval_between(self):
        from cocktail.schema.expressions import Expression

        # TODO: solve invalid operand order

        def between(x, i, j, **kwargs):
            return Expression.wrap(x).between(i, j, **kwargs).eval({})

        # Discrete values
        assert not between(1, 1, 1)
        assert not between(1, 1, 1, excludemin = True)
        assert between(1, 1, 1, excludemax = False)
        assert not between(1, 1, 1, excludemin = True, excludemax = False)

        assert between(1, 1, 2)
        assert not between(2, 1, 2)
        assert between(2, 1, 3)
        assert not between(1, 1, 2, excludemin = True)
        assert between(2, 1, 2, excludemax = False)

        # None value
        assert not between(None, 10, 25)
        assert not between(None, 10, None)
        assert between(None, None, 3)
        assert not between(None, None, 3, excludemin = True)

        # Infinite lower bound
        assert between(-175, None, 0)

        # Infinite upper bound
        assert between(175, 0, None)

        # Infinite bounds (lower and upper)
        assert between(0, None, None)
        assert between(None, None, None)
        assert not between(None, None, None, excludemin = True)

    def test_eval_range_intersection(self):
        
        # TODO: solve invalid operand order

        from cocktail.schema.expressions import RangeIntersectionExpression

        def intersect(a, b, c, d, **kwargs):
            return RangeIntersectionExpression(a, b, c, d, **kwargs).eval({})
        
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
        assert not intersect(1, 2, 2, 3, excludemin = True)
        assert intersect(3, 4, 2, 3, excludemax = False)

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
        assert not intersect(1, 1, 1, 1, excludemin = True) 
        assert intersect(1, 1, 1, 1, excludemax = False)
        assert not intersect(1, 1, 1, 1, excludemin = True, excludemax = False) 

        assert intersect(1, 2, 1, 2)
        assert intersect(1, 2, 1, 2, excludemin = True)
        assert intersect(1, 5, 1, 5, excludemin = True)
        assert intersect(1, 2, 1, 2, excludemax = True)
        assert intersect(1, 2, 1, 2, excludemin = True, excludemax = True)

        assert intersect(None, None, None, None)
        assert intersect(None, None, None, None, excludemin = True)
        assert intersect(None, None, None, None, excludemax = False)
        assert intersect(None, None, None, None,
            excludemin = True,
            excludemax = False
        )

        assert intersect(None, 1, None, 1)
        assert intersect(None, 1, None, 1, excludemin = True)
        assert intersect(None, 1, None, 1, excludemax = False)
        assert intersect(None, 1, None, 1,
            excludemin = True,
            excludemax = False
        )

        assert intersect(1, None, 1, None)
        assert intersect(1, None, 1, None, excludemin = True)
        assert intersect(1, None, 1, None, excludemax = False)
        assert intersect(1, None, 1, None,
            excludemin = True,
            excludemax = False
        )

        # Partial overlap
        assert intersect(1, 3, 2, 4)
        assert intersect(2, 4, 1, 3)
        assert intersect(None, 5, 3, None)
        assert intersect(3, None, None, 5)

    def test_eval_isinstance(self):
        from cocktail.schema.expressions import IsInstanceExpression
        from cocktail.persistence import PersistentObject, datastore

        datastore.root.clear()

        class A(PersistentObject):
            pass

        class B(PersistentObject):
            pass

        class C(A):
            pass

        a = A()
        b = B()
        c = C()

        assert IsInstanceExpression(c, C).eval({})
        assert IsInstanceExpression(c, A).eval({})
        assert IsInstanceExpression(a, A, is_inherited = False).eval({})

        assert IsInstanceExpression(c, (A, B)).eval({})
        assert not IsInstanceExpression(c, (A, B), is_inherited = False).eval({})
        assert IsInstanceExpression(c, (C, B)).eval({})
        assert not IsInstanceExpression(a, (C, B)).eval({})

    def test_eval_not_isinstance(self):
        from cocktail.schema.expressions import IsNotInstanceExpression
        from cocktail.persistence import PersistentObject, datastore

        datastore.root.clear()

        class A(PersistentObject):
            pass

        class B(PersistentObject):
            pass

        class C(A):
            pass

        a = A()
        b = B()
        c = C()

        assert IsNotInstanceExpression(a, B).eval({})
        assert not IsNotInstanceExpression(a, A).eval({})
        assert not IsNotInstanceExpression(c, A).eval({})
        assert IsNotInstanceExpression(c, A, is_inherited = False).eval({})

        assert IsNotInstanceExpression(b, (A, C)).eval({})
        assert not IsNotInstanceExpression(c, (B, A)).eval({})
        assert IsNotInstanceExpression(c, (B, A), is_inherited = False).eval({})


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

    def test_eval_descends_from_one_to_one_bidirectional(self):
        from cocktail.schema.expressions import DescendsFromExpression

        a = self.Document()
        b = self.Document()
        c = self.Document()

        a.extension = b
        b.extension = c

        assert DescendsFromExpression(a, a, self.Document.extension).eval({})
        assert not DescendsFromExpression(
            a, a, self.Document.extension, include_self = False
        ).eval({})
        assert DescendsFromExpression(b, a, self.Document.extension).eval({})
        assert DescendsFromExpression(c, a, self.Document.extension).eval({})
        assert not DescendsFromExpression(a, b, self.Document.extension).eval({})
        assert not DescendsFromExpression(b, c, self.Document.extension).eval({})

    def test_eval_descends_from_one_to_many_bidirectional(self):
        from cocktail.schema.expressions import DescendsFromExpression
        
        a = self.Document()
        b = self.Document()
        c = self.Document()
        d = self.Document()
        e = self.Document()

        a.children = [b, c]
        b.children = [d, e]

        assert DescendsFromExpression(a, a, self.Document.children).eval({})
        assert not DescendsFromExpression(
            a, a, self.Document.extension, include_self = False
        ).eval({})
        assert DescendsFromExpression(b, a, self.Document.children).eval({})
        assert not DescendsFromExpression(a, b, self.Document.children).eval({})
        assert DescendsFromExpression(d, a, self.Document.children).eval({})
        assert not DescendsFromExpression(c, b, self.Document.children).eval({})
        assert not DescendsFromExpression(d, c, self.Document.children).eval({})

    def test_eval_descends_from_one_to_one(self):
        from cocktail.schema.expressions import DescendsFromExpression

        a = self.Document()
        b = self.Document()
        c = self.Document()

        a.improvement = b
        b.improvement = c

        assert DescendsFromExpression(a, a, self.Document.improvement).eval({})
        assert not DescendsFromExpression(
            a, a, self.Document.extension, include_self = False
        ).eval({})
        assert DescendsFromExpression(b, a, self.Document.improvement).eval({})
        assert DescendsFromExpression(c, a, self.Document.improvement).eval({})
        assert not DescendsFromExpression(a, b, self.Document.improvement).eval({})
        assert not DescendsFromExpression(b, c, self.Document.improvement).eval({})

    def test_eval_descends_from_many_to_many(self):
        from cocktail.schema.expressions import DescendsFromExpression

        a = self.Document()
        b = self.Document()
        c = self.Document()
        d = self.Document()
        e = self.Document()

        a.related_documents = [b, c]
        b.related_documents = [d, e]

        assert DescendsFromExpression(a, a, self.Document.related_documents).eval({})
        assert not DescendsFromExpression(
            a, a, self.Document.extension, include_self = False
        ).eval({})
        assert DescendsFromExpression(c, a, self.Document.related_documents).eval({})
        assert DescendsFromExpression(d, a, self.Document.related_documents).eval({})
        assert not DescendsFromExpression(d, c, self.Document.related_documents).eval({})
        assert not DescendsFromExpression(a, b, self.Document.related_documents).eval({})

