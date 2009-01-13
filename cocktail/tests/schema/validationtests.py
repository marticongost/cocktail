#-*- coding: utf-8 -*-
"""

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
        correct_values,
        incorrect_values,
        error_type,
        error_attributes = None,
        error_count = 1):

        from cocktail.schema import Schema      

        for value in correct_values:
            assert member.validate(value), \
                "%r is a valid value" % value
            assert not list(member.get_errors(value))

        for value in incorrect_values:            
            assert not member.validate(value), \
                "%r is not a valid value" % value
            errors = list(member.get_errors(value))
            assert len(errors) == error_count
            error = errors[0]
            assert isinstance(error, error_type), \
                "%r is an instance of %r" % (error, error_type)
            #assert error.member is member
            
            if error_attributes:
                for attrib_key, attrib_value in error_attributes.iteritems():
                    assert getattr(error, attrib_key) == attrib_value

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

    def test_exclusive_callable(self):

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


if __name__ == "__main__":
    from unittest import main
    main()

