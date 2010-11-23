#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from unittest import TestCase
from cocktail import schema
from cocktail.persistence import PersistentObject
from cocktail.persistence.pickling import dumps, loads
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin

class A(PersistentObject):
    b = schema.String()
    c = schema.Integer()
    d = schema.Schema()

class PicklingTestCase(TempStorageMixin, TestCase):

    def _rebuild(self, obj):
        return loads(dumps(obj))

    def test_loaded_members_retain_identity(self):
        assert self._rebuild(A.b) is A.b

    def test_loaded_schemas_retain_identity(self):
        assert self._rebuild(A.d) is A.d

    def test_loaded_persistent_objects_retain_identity(self):
        a = A()
        a.b = "foo"
        a.c = 3
        a.insert()

        b = self._rebuild(a)

        assert b is a
        assert b.b is a.b
        assert b.c is a.c
        assert b.d is a.d

    def test_serialized_queries_retain_type(self):
        assert self._rebuild(A.select()).type is A

    def test_serialized_queries_retain_base_collection(self):
        q = A.select()
        q.base_collection = [1, 2, 3]
        assert self._rebuild(q).base_collection == q.base_collection

    def test_serialized_queries_retain_filters(self):
        q = A.select([A.b.equal("foo"), A.c.greater(4)])
        assert self._rebuild(q).filters == q.filters

    def test_serialized_queries_retain_order(self):
        
        q = A.select(order = A.b)
        assert self._rebuild(q).order == q.order
        
        q = A.select(order = A.c.negative())
        assert self._rebuild(q).order == q.order

        q = A.select(order = [A.b.negative(), A.c])
        assert self._rebuild(q).order == q.order

    def test_serialized_queries_retain_range(self):
        q = A.select(range = (0, 10))
        assert self._rebuild(q).range == q.range

    def test_serialized_queries_retain_attributes(self):
 
        q = A.select(
            filters = [A.b.equal("foo"), A.c.greater(4)],
            order = [A.b, A.c.negative()],
            range = (5, 25)
        )
        q.base_collection = [1, 2, 3]
        
        rq = self._rebuild(q)
        
        assert rq.type is A
        assert rq.base_collection == q.base_collection
        assert rq.filters == q.filters
        assert rq.order == q.order
        assert rq.range == q.range

