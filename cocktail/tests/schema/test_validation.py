#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""

from unittest import TestCase

class ValidationTestCase(TestCase):

    def _test_validation(
        self,
        member,
        correct_values = None,
        incorrect_values = None,
        error_type = None,
        error_attributes = None,
        error_count = 1):

        from cocktail.schema import Schema      

        if correct_values:
            for value in correct_values:
                assert member.validate(value), \
                    "%r should be a valid value. Errors:\n\t%s" % (
                        value,
                        "\n\t".join(
                                str(error)
                                for error in member.get_errors(value)
                            )
                    )
                assert not list(member.get_errors(value))

        if incorrect_values:
            for value in incorrect_values:            
                assert not member.validate(value), \
                    "%r shouldn't be a valid value" % value
                errors = list(member.get_errors(value))
                self.assertEqual(len(errors), error_count)
                error = errors[0]
                assert isinstance(error, error_type), \
                    "%r should be an instance of %r" % (error, error_type)
                #assert error.member is member
                
                if error_attributes:
                    for attrib_key, attrib_value \
                    in error_attributes.iteritems():
                        assert getattr(error, attrib_key) == attrib_value


class DuplicatedValidationsTestCase(TestCase):

    def test_duplicated_validations(self):

        from cocktail.schema import Member

        def a(): pass
        def b(): pass

        m = Member()
        m.add_validation(a)
        m.add_validation(b)
        v1 = list(m.validations())
        m.add_validation(a)
        v2 = list(m.validations())
        assert v1 == v2

    def test_add_duplicated_validation_to_derived_schema(self):

        from cocktail.schema import Schema

        def a(): pass

        s1 = Schema()
        s1.add_validation(a)
        
        s2 = Schema()
        s2.inherit(s1)
        v1 = list(s2.validations())
        s2.add_validation(a)
        v2 = list(s2.validations())
         
        assert v1 == v2

    def test_add_duplicated_validation_to_base_schema(self):

        from cocktail.schema import Schema

        def a(): pass

        s1 = Schema()
        
        s2 = Schema()
        s2.inherit(s1)
        s2.add_validation(a)

        v1 = list(s2.validations())
        s1.add_validation(a)
        v2 = list(s2.validations())
                
        assert v1 == v2    


class MemberValidationTestCase(ValidationTestCase):
    
    def test_required(self):

        from cocktail.schema import Member, exceptions

        self._test_validation(
            Member(required = True),
            [1, 0, -2, "a", "hello world!!", "", [], {}],
            [None],
            exceptions.ValueRequiredError
        )

    def test_require_none(self):

        from cocktail.schema import Member, exceptions

        self._test_validation(
            Member(require_none = True),
            [None],
            [1, 0, -2, "a", "hello world!!", "", [], {}],
            exceptions.NoneRequiredError
        )

    def test_type(self):

        from cocktail.schema import Member, exceptions

        self._test_validation(
            Member(type = basestring),
            [None, "hello world", u"Hola món!", ""],
            [15, 0, [], ["hello world"], {}],
            exceptions.TypeCheckError,
            {"type": basestring}
        )

        self._test_validation(
            Member(type = float),
            [None, 1.5, 27.104, 12.8],
            ["", "hello!", 2, {}, [1.5, 27.3]],
            exceptions.TypeCheckError,
            {"type": float}
        )

    def test_enumeration(self):

        from cocktail.schema import Member, exceptions

        self._test_validation(
            Member(enumeration = ["cherry", "apple", "peach"]),            
            [None, "cherry", "apple", "peach"],
            ["coconut", "watermelon", "banana"],
            exceptions.EnumerationError
        )


class InheritedValidationsTestCase(TestCase):

    def _add_error(self, schema):
        
        from cocktail.schema.exceptions import ValidationError

        def validation(member, validable, context):
            yield ValidationError(schema, validable, context)

        schema.add_validation(validation)

    def test_single_inheritance(self):

        from cocktail.schema import Schema

        base = Schema()
        self._add_error(base)

        derived = Schema()
        derived.inherit(base)
    
        errors = list(derived.get_errors({}))
        assert len(errors) == 1
        assert errors[0].member == base

    def test_base_isolation(self):

        from cocktail.schema import Schema

        base = Schema()

        derived = Schema()
        self._add_error(derived)
        derived.inherit(base)
    
        assert not list(base.get_errors({}))

    def test_multiple_inheritance(self):

        from cocktail.schema import Schema

        base1 = Schema()
        self._add_error(base1)

        base2 = Schema()
        self._add_error(base2)

        derived = Schema()
        derived.inherit(base1)
        derived.inherit(base2)
    
        errors = list(derived.get_errors({}))
        assert len(errors) == 2
        assert errors[0].member == base1
        assert errors[1].member == base2

    def test_deep_inheritance(self):

        from cocktail.schema import Schema

        s1 = Schema()
        self._add_error(s1)

        s2 = Schema()
        s2.inherit(s1)
        self._add_error(s2)

        s3 = Schema()
        s3.inherit(s2)
        self._add_error(s3)

        s4 = Schema()
        s4.inherit(s3)
            
        errors = list(s4.get_errors({}))
        assert len(errors) == 3
        assert errors[0].member == s1
        assert errors[1].member == s2
        assert errors[2].member == s3


class StringValidationTestCase(ValidationTestCase):

    def test_min(self):

        from cocktail.schema import String, exceptions

        self._test_validation(
            String(min = 5),
            [None, "hello", "strange", ", strange world!!"],
            ["", "hulo", "hum"],
            exceptions.MinLengthError
        )

    def test_max(self):
        
        from cocktail.schema import String, exceptions

        self._test_validation(
            String(max = 5),
            [None, "", "hi", "hulo", "hello"],
            ["greetings", "welcome"],
            exceptions.MaxLengthError
        )

    def test_format(self):

        from cocktail.schema import String, exceptions

        self._test_validation(
            String(format = r"^\d{4}-\d{2}[a-zA-Z]$"),
            [None, "4261-85M", "7508-34x"],
            ["", "Bugger numeric codes", "AAADSADS20934832498234"],
            exceptions.FormatError
        )

class IntegerValidationTestCase(ValidationTestCase):

    def test_min(self):

        from cocktail.schema import Integer, exceptions

        self._test_validation(
            Integer(min = 5),
            [None, 5, 6, 15, 300],
            [4, 3, 0, -2, -100],
            exceptions.MinValueError
        )    

    def test_max(self):

        from cocktail.schema import Integer, exceptions

        self._test_validation(
            Integer(max = 5),
            [None, 5, 4, 0, -6, -78],
            [6, 7, 15, 100, 300],
            exceptions.MaxValueError
        )


class RelationValidationTestCase(ValidationTestCase):

    def test_reference_relation_constraints(self):

        from cocktail.schema import Reference, Integer, exceptions, get

        foreign_field = Integer("foo")

        ref = Reference(relation_constraints = [
            foreign_field.not_equal(None),
            foreign_field.greater(3),
            foreign_field.lower(8),
            lambda owner, related: get(related, "foo", None) is None
                or get(related, "foo", None) % 5 != 0
        ])

        self._test_validation(
            ref,
            [None, {"foo": 4}, {"foo": 6}, {"foo": 7}]
        )

        self._test_validation(
            ref,
            None,
            [{}, {"foo": None}],
            exceptions.RelationConstraintError,
            error_count = 2 # Note that x > None is always True
        )

        self._test_validation(
            ref,
            None,
            [{"foo": -6}, {"foo": 1}, {"foo": 3}],
            exceptions.RelationConstraintError,
            {"constraint": ref.relation_constraints[1]}
        )

        self._test_validation(
            ref,
            None,
            [{"foo": 8}, {"foo": 12}, {"foo": 134}],
            exceptions.RelationConstraintError,
            {"constraint": ref.relation_constraints[2]}
        )

        self._test_validation(
            ref,
            None,
            [{"foo": 5}],
            exceptions.RelationConstraintError,
            {"constraint": ref.relation_constraints[3]}
        )

    def test_collection_relation_constraints(self):

        from cocktail.schema import Collection, Integer, exceptions, get

        foreign_field = Integer("foo")

        collection = Collection(relation_constraints = [
            foreign_field.not_equal(None),
            foreign_field.greater(3),
            foreign_field.lower(8),
            lambda owner, related: get(related, "foo", None) is None
                or get(related, "foo", None) % 5 != 0
        ])

        self._test_validation(
            collection,
            [[], [None], [{"foo": 4}, {"foo": 6}], [{"foo": 4}, {"foo": 7}]]
        )

        self._test_validation(
            collection,
            None,
            [[{}], [{"foo": None}], [{"foo": 6}, {}]],
            exceptions.RelationConstraintError,
            error_count = 2 # Note that x > None is always True
        )

        self._test_validation(
            collection,
            None,
            [[{"foo": -6}, {"foo": 1}, {"foo": 3}]],
            exceptions.RelationConstraintError,
            {"constraint": collection.relation_constraints[1]},
            error_count = 3
        )

        self._test_validation(
            collection,
            None,
            [[{"foo": 8}, {"foo": 12}, {"foo": 134}]],
            exceptions.RelationConstraintError,
            {"constraint": collection.relation_constraints[2]},
            error_count = 3
        )

        self._test_validation(
            collection,
            None,
            [[{"foo": 5}]],
            exceptions.RelationConstraintError,
            {"constraint": collection.relation_constraints[3]}
        )

        
class CollectionValidationTestCase(ValidationTestCase):

    def test_min(self):
        
        from cocktail.schema import Collection, exceptions

        self._test_validation(
            Collection(min = 3, required = False),
            [None, [1, 2, 3], ["a", "b", "c", "d"], range(50)],
            [[], ["a"], [1, 2]],
            exceptions.MinItemsError
        )

    def test_max(self):

        from cocktail.schema import Collection, exceptions

        self._test_validation(
            Collection(max = 3, required = False),
            [None, [], ["a"], (1, 2), set([1, 2, 3])],
            [["a", "b", "c", "d"], range(10)],
            exceptions.MaxItemsError
        )

    def test_items(self):

        from cocktail.schema import Collection, Integer, exceptions

        self._test_validation(
            Collection(items = Integer(), required = False),
            [None, [], [1], [1, 2], set([1, 2, 3]), tuple(range(10))],
            [["a", "b", "c"], [3.5, 2.7, 1.4]],
            exceptions.TypeCheckError,
            error_count = 3
        )

    def test_cycles_allowed(self):

        from cocktail.schema import Reference, exceptions

        # Valid relations
        a = {"rel": None}
        b = {"rel": a}
        
        # 'c' contains itself
        c = {"rel": None}
        c["rel"] = c
        
        # 'd' and 'e' form a cycle
        d = {"rel": None}
        e = {"rel": None}
        d["rel"] = e
        e["rel"] = d

        # 'f' and 'h' form a cycle
        f = {"rel": None}
        g = {"rel": None}
        h = {"rel": None}
        f["rel"] = g
        g["rel"] = h
        h["rel"] = f

        self._test_validation(
            Reference("rel", cycles_allowed = False),
            [a, b],
            [c, d, e, f, g, h],
            exceptions.RelationCycleError
        )

        self._test_validation(
            Reference("rel", cycles_allowed = True),
            [a, b, c, d, e, f, g, h]
        )


class SchemaValidationTestCase(ValidationTestCase):

    def test_scalar(self):

        from cocktail.schema import Schema, Integer, exceptions
        
        class Validable(object):
            def __init__(self, foo):
                self.foo = foo

            def __repr__(self):
                return "Validable(%r)" % self.foo

        self._test_validation(
            Schema(members = {
                "foo": Integer()
            }),
            [Validable(None), Validable(1), Validable(15)],
            [Validable(""), Validable("hello, world!"), Validable(3.15)],
            exceptions.TypeCheckError
        )

    def test_translated(self):
        
        from cocktail.schema import Schema, String, exceptions

        schema = Schema()
        schema.add_member(String("foo", translated = True, required = True))

        validable = {
            "foo": {"ca": "Hola", "es": "Hola", "en": "Hello"}
        }

        assert not list(schema.get_errors(validable))

        validable["foo"]["fr"] = None
        validable["foo"]["es"] = None

        errors = list(schema.get_errors(validable))
        assert len(errors) == 2
        assert set([error.language for error in errors]) == set(["fr", "es"])


class DynamicConstraintsTestCase(TestCase):

    def test_callable(self):

        from cocktail.schema import Schema, String, Boolean
        from cocktail.schema.exceptions import ValueRequiredError
        
        test_schema = Schema()
        test_schema.add_member(Boolean("enabled"))
        test_schema.add_member(
            String("field", required = lambda ctx: ctx.get_value("enabled"))
        )

        assert test_schema.validate({"enabled": False, "field": None})
        assert test_schema.validate({"enabled": True, "field": "foo"})
        
        errors = list(test_schema.get_errors({"enabled": True, "field": None}))
        assert len(errors) == 1
        error = errors[0]
        assert isinstance(error, ValueRequiredError)

    def test_expression(self):

        from cocktail.schema import Schema, String, Boolean
        from cocktail.schema.exceptions import ValueRequiredError
        
        test_schema = Schema()
        test_schema.add_member(Boolean("enabled"))
        test_schema.add_member(
            String("field", required = test_schema["enabled"])
        )

        assert test_schema.validate({"enabled": False, "field": None})
        assert test_schema.validate({"enabled": True, "field": "foo"})
        
        errors = list(test_schema.get_errors({"enabled": True, "field": None}))
        assert len(errors) == 1
        error = errors[0]
        assert isinstance(error, ValueRequiredError)

    def test_exclusive_callable(self):

        from cocktail.schema import Schema, String, Boolean
        from cocktail.schema.exceptions import (
            ValueRequiredError,
            NoneRequiredError
        )
        
        test_schema = Schema()
        test_schema.add_member(Boolean("enabled"))
        test_schema.add_member(
            String("field", exclusive = lambda ctx: ctx.get_value("enabled"))
        )

        # Valid states
        assert test_schema.validate({"enabled": False, "field": None})
        assert test_schema.validate({"enabled": True, "field": "foo"})
        
        # None required error
        errors = list(test_schema.get_errors({
            "enabled": False, "field": "foo"
        }))
        assert len(errors) == 1
        error = errors[0]
        assert isinstance(error, NoneRequiredError)

        # Required error
        errors = list(test_schema.get_errors({"enabled": True, "field": None}))
        assert len(errors) == 1
        error = errors[0]
        assert isinstance(error, ValueRequiredError)

    def test_exclusive_expression(self):

        from cocktail.schema import Schema, String, Boolean
        from cocktail.schema.exceptions import (
            ValueRequiredError,
            NoneRequiredError
        )
        
        test_schema = Schema()
        test_schema.add_member(Boolean("enabled"))
        test_schema.add_member(
            String("field", exclusive = test_schema["enabled"])
        )

        # Valid states
        assert test_schema.validate({"enabled": False, "field": None})
        assert test_schema.validate({"enabled": True, "field": "foo"})
        
        # None required error
        errors = list(test_schema.get_errors({
            "enabled": False, "field": "foo"
        }))
        assert len(errors) == 1
        error = errors[0]
        assert isinstance(error, NoneRequiredError)

        # Required error
        errors = list(test_schema.get_errors({"enabled": True, "field": None}))
        assert len(errors) == 1
        error = errors[0]
        assert isinstance(error, ValueRequiredError)

