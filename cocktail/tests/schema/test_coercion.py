"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from unittest import TestCase


class ScalarFieldCoercionTestCase(TestCase):

    invalid_values = [None, "", "Foobar", 3]
    valid_values = [10, 333]

    def setUp(self):
        from cocktail.schema import Integer
        self.member = Integer(required=True, min=5, default=50)

    def test_can_ignore_errors(self):

        from cocktail.schema import Coercion

        for value in self.invalid_values:
            assert self.member.coerce(value, Coercion.NONE) == value

        for value in self.valid_values:
            assert self.member.coerce(value, Coercion.NONE) == value

    def test_can_replace_invalid_values_with_none(self):

        from cocktail.schema import Coercion

        for value in self.invalid_values:
            assert self.member.coerce(value, Coercion.SET_NONE) is None

        for value in self.valid_values:
            assert self.member.coerce(value, Coercion.SET_NONE) == value

    def test_can_replace_invalid_values_with_default(self):

        from cocktail.schema import Coercion

        for value in self.invalid_values:
            assert self.member.coerce(value, Coercion.SET_DEFAULT) \
                == self.member.default

        for value in self.valid_values:
            assert self.member.coerce(value, Coercion.SET_DEFAULT) == value

    def test_can_raise_errors_immediately(self):

        from cocktail.schema import Coercion
        from cocktail.schema.exceptions import ValidationError

        for value in self.invalid_values:
            try:
                self.member.coerce(value, Coercion.FAIL_IMMEDIATELY)
            except ValidationError:
                pass
            else:
                raise AssertionError(
                    f"Coercing {value} should raise a validation error"
                )

        for value in self.valid_values:
            assert self.member.coerce(value, Coercion.FAIL_IMMEDIATELY) \
                == value

    def test_can_aggregate_errors(self):

        from cocktail.schema import Coercion
        from cocktail.schema.exceptions import CoercionError

        for value in self.invalid_values:
            try:
                self.member.coerce(value, Coercion.FAIL)
            except CoercionError as e:
                assert e.member is self.member
                assert e.errors
            else:
                raise AssertionError(
                    f"Coercing {value} should raise a coercion error"
                )

        for value in self.valid_values:
            assert self.member.coerce(value, Coercion.FAIL) == value


class SchemaCoercionTestCase(TestCase):

    def setUp(self):
        from cocktail.schema import Schema, Integer, String
        self.schema = Schema(members=[
            Integer("num", required=True, min=5, default=50),
            String("text", min=5, default="cornucopia")
        ])

    def test_can_ignore_errors(self):

        from itertools import product
        from cocktail.schema import Coercion

        for obj in [
            {"num": 3, "text": None},
            {"num": 20, "text": "hum"},
            {"num": 3, "text": "hum"},
            {"num": 15, "text": "spam!"}
        ]:
            original = obj.copy()
            result = self.schema.coerce(obj, Coercion.NONE)
            assert result is obj
            assert result == original

    def test_can_replace_invalid_values_with_none(self):

        from cocktail.schema import Coercion

        # num invalid, text valid
        obj = {"num": 3, "text": None}
        result = self.schema.coerce(obj, Coercion.SET_NONE)
        assert obj is result
        assert result == {"num": None, "text": None}

        # num valid, text invalid
        obj = {"num": 20, "text": "hum"}
        result = self.schema.coerce(obj, Coercion.SET_NONE)
        assert obj is result
        assert result == {"num": 20, "text": None}

        # both invalid
        obj = {"num": 3, "text": "hum"}
        result = self.schema.coerce(obj, Coercion.SET_NONE)
        assert obj is result
        assert result == {"num": None, "text": None}

        # both valid
        obj = {"num": 15, "text": "spam!"}
        result = self.schema.coerce(obj, Coercion.SET_NONE)
        assert obj is result
        assert result == {"num": 15, "text": "spam!"}

    def test_can_replace_invalid_values_with_default(self):

        from cocktail.schema import Coercion

        default_num = self.schema["num"].default
        default_text = self.schema["text"].default

        # num invalid, text valid
        obj = {"num": 3, "text": None}
        result = self.schema.coerce(obj, Coercion.SET_DEFAULT)
        assert obj is result
        assert result == {"num": default_num, "text": None}

        # num valid, text invalid
        obj = {"num": 20, "text": "hum"}
        result = self.schema.coerce(obj, Coercion.SET_DEFAULT)
        assert obj is result
        assert result == {"num": 20, "text": default_text}

        # both invalid
        obj = {"num": 3, "text": "hum"}
        result = self.schema.coerce(obj, Coercion.SET_DEFAULT)
        assert obj is result
        assert result == {"num": default_num, "text": default_text}

        # both valid
        obj = {"num": 15, "text": "spam!"}
        result = self.schema.coerce(obj, Coercion.SET_DEFAULT)
        assert obj is result
        assert result == {"num": 15, "text": "spam!"}

    def test_can_raise_errors_immediately(self):

        from cocktail.schema import Coercion
        from cocktail.schema.exceptions import ValidationError

        FI = Coercion.FAIL_IMMEDIATELY

        # num invalid, text valid
        obj = {"num": 3, "text": None}
        try:
            self.schema.coerce(obj, FI)
        except ValidationError as e:
            assert e.member is self.schema["num"]
        else:
            raise AssertionError(
                f"Coercing {obj} should raise a validation error on 'num'"
            )

        # num valid, text invalid
        obj = {"num": 20, "text": "hum"}
        try:
            self.schema.coerce(obj, FI)
        except ValidationError as e:
            assert e.member is self.schema["text"]
        else:
            raise AssertionError(
                f"Coercing {obj} should raise a validation error on 'text'"
            )

        # both invalid
        obj = {"num": 3, "text": "hum"}
        try:
            self.schema.coerce(obj, FI)
        except ValidationError as e:
            pass
        else:
            raise AssertionError(
                f"Coercing {obj} should raise a validation error"
            )

        # both valid
        obj = {"num": 15, "text": "spam!"}
        original = obj.copy()
        result = self.schema.coerce(obj, FI)
        assert obj is result
        assert result == original

    def test_can_aggregate_errors(self):

        from cocktail.schema import Coercion
        from cocktail.schema.exceptions import CoercionError

        def bad_keys(e):
            keys = set()
            for error in e.errors:
                keys.update(member.name for member in error.invalid_members)
            return keys

        # num invalid, text valid
        obj = {"num": 3, "text": None}
        try:
            self.schema.coerce(obj, Coercion.FAIL)
        except CoercionError as e:
            assert bad_keys(e) == {"num"}
        else:
            raise AssertionError(
                f"Coercing {obj} should raise a validation error on 'num'"
            )

        # num valid, text invalid
        obj = {"num": 20, "text": "hum"}
        try:
            self.schema.coerce(obj, Coercion.FAIL)
        except CoercionError as e:
            assert bad_keys(e) == {"text"}
        else:
            raise AssertionError(
                f"Coercing {obj} should raise a validation error on 'text'"
            )

        # both invalid
        obj = {"num": 3, "text": "hum"}
        try:
            self.schema.coerce(obj, Coercion.FAIL)
        except CoercionError as e:
            assert bad_keys(e) == {"num", "text"}
        else:
            raise AssertionError(
                f"Coercing {obj} should raise a validation error"
            )

        # both valid
        obj = {"num": 15, "text": "spam!"}
        original = obj.copy()
        result = self.schema.coerce(obj, Coercion.FAIL)
        assert obj is result
        assert result == original

