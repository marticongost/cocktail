#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class BaseTestCase(TestCase):

    def setUp(self):

        from cocktail.schema import String
        from cocktail.persistence import PersistentObject

        class TestModel(PersistentObject):
            
            unique_field = String(
                unique = True,
                indexed = True
            )

            unique_field_2 = String(
                unique = True,
                indexed = True
            )

            indexed_field = String(
                indexed = True
            )

            regular_field = String()

        self.TestModel = TestModel


class PersistentObjectGetInstanceTestCase(TempStorageMixin, BaseTestCase):

    def setUp(self):                
        TempStorageMixin.setUp(self)
        BaseTestCase.setUp(self)

    def test_get_by_id(self):
        
        a = self.TestModel()
        a.insert()
        
        b = self.TestModel()
        b.insert()

        c = self.TestModel()
        c.insert()

        # Explicit field
        self.assertTrue(self.TestModel.get_instance(id = a.id) is a)
        self.assertTrue(self.TestModel.get_instance(id = b.id) is b)
        self.assertTrue(self.TestModel.get_instance(id = c.id) is c)
        self.assertTrue(self.TestModel.get_instance(id = c.id + 1) is None)

        # Implicit field
        self.assertTrue(self.TestModel.get_instance(a.id) is a)
        self.assertTrue(self.TestModel.get_instance(b.id) is b)
        self.assertTrue(self.TestModel.get_instance(c.id) is c)
        self.assertTrue(self.TestModel.get_instance(c.id + 1) is None)

    def test_get_by_unique_field(self):

        a = self.TestModel()
        a.unique_field = "A"
        a.insert()

        b = self.TestModel()
        b.unique_field = "B"
        b.insert()
        
        c = self.TestModel()
        c.unique_field = "C"
        c.insert()

        self.assertTrue(
            self.TestModel.get_instance(unique_field = a.unique_field) is a)
        
        self.assertTrue(
            self.TestModel.get_instance(unique_field = b.unique_field) is b)
        
        self.assertTrue(
            self.TestModel.get_instance(unique_field = c.unique_field) is c)

        self.assertTrue(
            self.TestModel.get_instance(unique_field = "Z") is None)

        # Mixing positional and keyword arguments is not allowed
        self.assertRaises(
            ValueError,
            self.TestModel.get_instance,
            1,
            unique_field = "A"
        )

        # Querying by more than one field is not allowed
        self.assertRaises(
            ValueError,
            self.TestModel.get_instance,
            unique_field = "A",
            unique_field_2 = "C"
        )

    def test_get_by_non_unique_field(self):

        a = self.TestModel()
        a.indexed_field = "A"
        a.insert()

        b = self.TestModel()
        b.regular_field = "B"
        b.insert()
        
        self.assertRaises(ValueError, a.get_instance, indexed_field = "A")
        self.assertRaises(ValueError, a.get_instance, indexed_field = "Z")
        self.assertRaises(ValueError, b.get_instance, regular_field = "B")
        self.assertRaises(ValueError, b.get_instance, regular_field = "Z")


class PersistentObjectSelectTestCase(BaseTestCase):

    def test_select_empty(self):

        from cocktail.persistence.query import Query
        
        query = self.TestModel.select()
        self.assertTrue(isinstance(query, Query))
        self.assertEqual(query.type, self.TestModel)
        self.assertFalse(query.filters)
        self.assertFalse(query.order)
        self.assertFalse(query.range)

    def test_select_expression(self):

        from cocktail.persistence.query import Query

        expr = self.TestModel.unique_field.equal("A")
        query = self.TestModel.select(expr)
        self.assertTrue(isinstance(query, Query))
        self.assertEqual(query.type, self.TestModel)
        self.assertEqual(list(query.filters), [expr])

    def test_select_expression_list(self):

        from cocktail.persistence.query import Query

        expr1 = self.TestModel.indexed_field.equal("A")
        expr2 = self.TestModel.regular_field.equal("B")
        query = self.TestModel.select([expr1, expr2])
        self.assertTrue(isinstance(query, Query))
        self.assertEqual(query.type, self.TestModel)
        self.assertEqual(list(query.filters), [expr1, expr2])

    def test_select_map(self):

        from cocktail.schema import Member
        from cocktail.schema.expressions import EqualExpression
        from cocktail.persistence.query import Query

        params = {
            "unique_field": "A",
            "indexed_field": "spam"
        }

        query = self.TestModel.select(params)
        
        self.assertTrue(isinstance(query, Query))
        self.assertEqual(query.type, self.TestModel)
        self.assertEqual(len(query.filters), 2)

        for expr in query.filters:
            self.assertTrue(expr, EqualExpression)
            member = expr.operands[0]
            self.assertTrue(isinstance(member, Member))
            self.assertEqual(params[member.name], expr.operands[1].value)
            del params[member.name]

    def test_select_order_string(self):

        from cocktail.schema.expressions import (
            PositiveExpression, NegativeExpression
        )

        query = self.TestModel.select(order = "unique_field")
        self.assertEqual(len(query.order), 1)
        self.assertTrue(isinstance(query.order[0], PositiveExpression))
        self.assertTrue(
            query.order[0].operands[0] is self.TestModel.unique_field)

        query = self.TestModel.select(order = "+unique_field")
        self.assertEqual(len(query.order), 1)
        self.assertTrue(isinstance(query.order[0], PositiveExpression))
        self.assertTrue(
            query.order[0].operands[0] is self.TestModel.unique_field)

        query = self.TestModel.select(order = "-unique_field")
        self.assertEqual(len(query.order), 1)
        self.assertTrue(isinstance(query.order[0], NegativeExpression))
        self.assertTrue(
            query.order[0].operands[0] is self.TestModel.unique_field)

    def test_select_order_reference(self):

        from cocktail.schema.expressions import (
            PositiveExpression, NegativeExpression
        )

        query = self.TestModel.select(order = self.TestModel.unique_field)
        self.assertEqual(len(query.order), 1)
        self.assertTrue(isinstance(query.order[0], PositiveExpression))
        self.assertTrue(
            query.order[0].operands[0] is self.TestModel.unique_field)

        query = self.TestModel.select(
            order = self.TestModel.unique_field.positive())
        self.assertEqual(len(query.order), 1)
        self.assertTrue(isinstance(query.order[0], PositiveExpression))
        self.assertTrue(
            query.order[0].operands[0] is self.TestModel.unique_field)

        query = self.TestModel.select(
            order = self.TestModel.unique_field.negative())
        self.assertEqual(len(query.order), 1)
        self.assertTrue(isinstance(query.order[0], NegativeExpression))
        self.assertTrue(
            query.order[0].operands[0] is self.TestModel.unique_field)

    def test_select_order_string_collection(self):

        from cocktail.schema.expressions import (
            PositiveExpression, NegativeExpression
        )

        query = self.TestModel.select(
            order = ("+unique_field", "-unique_field_2", "regular_field"))
        self.assertEqual(len(query.order), 3)        
        
        self.assertTrue(isinstance(query.order[0], PositiveExpression))
        self.assertTrue(
            query.order[0].operands[0] is self.TestModel.unique_field)
        
        self.assertTrue(isinstance(query.order[1], NegativeExpression))
        self.assertTrue(
            query.order[1].operands[0] is self.TestModel.unique_field_2)

        self.assertTrue(isinstance(query.order[2], PositiveExpression))
        self.assertTrue(
            query.order[2].operands[0] is self.TestModel.regular_field)

    def test_select_range(self):
        self.assertEqual(
            self.TestModel.select(range = (0, 10)).range, (0, 10)
        )

        self.assertRaises(TypeError, self.TestModel.select, range = "foo")
        self.assertRaises(TypeError, self.TestModel.select, range = (None, 5))
        self.assertRaises(TypeError, self.TestModel.select, range = (1, "foo"))
        self.assertRaises(ValueError, self.TestModel.select, range = (-5,10))


class QueryOrderTestCase(TempStorageMixin, BaseTestCase):

    def setUp(self):

        from cocktail.persistence import Query

        TempStorageMixin.setUp(self)
        BaseTestCase.setUp(self)
       
        self.Query = Query

    def test_add_order(self):

        expr1 = self.TestModel.indexed_field.equal("A").positive()
        expr2 = self.TestModel.regular_field.greater("B").negative()
        expr3 = self.TestModel.unique_field.not_equal("C").positive()
        
        query = self.Query(self.TestModel, order = expr1)
        
        query.add_order(expr2)
        self.assertEqual(list(query.order), [expr1, expr2])

        query.add_order(expr3)
        self.assertEqual(list(query.order), [expr1, expr2, expr3])

    def test_order_single_criteria(self):

        instances = [self.TestModel(indexed_field = unicode(i))
                    for i in range(10)]

        for inst in instances:
            inst.insert()

        self.assertEqual(
            list(
                self.Query(
                    self.TestModel,
                    order = "indexed_field"
                )
            ),
            instances
        )

        self.assertEqual(
            list(
                self.Query(
                    self.TestModel,
                    order = "-indexed_field"
                )
            ),
            list(reversed(instances))
        )

        self.assertEqual(
            list(
                self.Query(
                    self.TestModel,
                    order = self.TestModel.indexed_field
                )
            ),
            instances
        )

        self.assertEqual(
            list(
                self.Query(
                    self.TestModel,
                    order = self.TestModel.indexed_field.positive()
                )
            ),
            instances
        )

        self.assertEqual(
            list(
                self.Query(
                    self.TestModel,
                    order = self.TestModel.indexed_field.negative()
                )
            ),
            list(reversed(instances))
        )

