#-*- coding: utf-8 -*-
u"""
Provides the base class for all schema members.
"""
from itertools import chain
from copy import deepcopy
from cocktail.events import Event, EventHub
from cocktail.modeling import ListWrapper, OrderedSet
from cocktail.pkgutils import import_object
from cocktail.translations import translations
from cocktail.schema import exceptions
from cocktail.schema.expressions import Expression, Variable
from cocktail.schema.validationcontext import ValidationContext
from cocktail.schema.accessors import get_accessor


class Member(Variable):
    """A member describes the properties and metadata of a unit of data.

    Although not strictly an abstract class, the class is very generic in
    nature, and is inherited by a wealth of other classes that add the
    necessary features to describe a variety of more concrete data types
    (`String`, `Integer`, `Boolean`, etc.).

    Members can also be composited, in order to describe parts of a more complex
    data set, by embedding them within a `Collection` or `Schema`.

    .. attribute:: default
    
        The default value for the member.
    
    .. attribute:: required
    
        Determines if the field requires a value. When set to true, a value of
        None for this member will trigger a validation error of type
        `exceptions.ValueRequiredError`.

    .. attribute:: require_none

        Determines if the field disallows any value other than None.  When set
        to true, a value different than None for this member will trigger a
        validation error of type `exceptions.NoneRequiredError`.
    
    .. attribute:: enumeration

        Establishes a limited set of acceptable values for the member. If a
        member with this constraint is given a value not found inside the set,
        an `exceptions.EnumerationError` error will be triggered.

    .. attribute:: translated

        Indicates if the member accepts multiple values, each in a different
        language.
    """
    __metaclass__ = EventHub

    attached = Event(
        doc = """An event triggered when the member is added to a schema."""
    )

    # Groupping
    member_group = None

    # Constraints
    primary = False
    default = None
    required = False
    require_none = False
    enumeration = None

    # Instance data layout
    accessor = None

    # Copying and adaptation
    _copy_class = None
    copy_source = None
    adaptation_source = None
    original_member = None

    # Translation
    translated = False
    translation = None
    translation_source = None
    
    # Attributes that deserve special treatment when performing a deep copy
    _special_copy_keys = set([
        "__class__", "_schema", "_validations_wrapper", "_validations"
    ])

    def __init__(self, name = None, doc = None, **kwargs):
        """Initializes a member, optionally setting its name, docstring and a
        set of arbitrary attributes.

        :param name: The `name` given to the member.
        :type name: str

        :param doc: The docstring to assign to the member.
        :type doc: unicode

        :param kwargs: A set of key/value pairs to set as attributes of the
            member.
        """
        self._name = None
        self._schema = None
        self._validations = OrderedSet()
        self._validations_wrapper = ListWrapper(self._validations)
        self.add_validation(Member.member_validation_rule)
        self.original_member = self

        Variable.__init__(self, None)
        self.__type = None

        self.name = name
        self.__doc__ = doc

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        
        member_desc = self._name \
            and "member '%s'" % self._name \
            or "anonymous " + self.__class__.__name__.lower()

        if self._schema is None:
            return "unbound " + member_desc
        else:
            schema_name = self._schema.name
            return "%s in %s" % (
                member_desc,
                schema_name
                    and "'%s' schema" % schema_name or "anonymous schema"
            )

    def _get_name(self):
        return self._name

    def _set_name(self, value):

        if self._schema is not None:
            raise exceptions.MemberRenamedError(self, value)
        
        self._name = value

    name = property(_get_name, _set_name, doc = 
        """The name that uniquely identifies the member on the schema it is
        bound to. Once set it can't be changed (trying to do so will raise a
        `exceptions.MemberRenamedError` exception).
        """)

    def _get_schema(self):
        return self._schema

    def _set_schema(self, value):

        if self._schema is not None:
            raise exceptions.MemberReacquiredError(self, value)

        self._schema = value

    schema = property(_get_schema, _set_schema, doc = 
        """The `schema <Schema>` that the member is bound to. Once set it can't
        be changed (doing so will raise a `exceptions.MemberReacquiredError`
        exception).
        """)

    def _get_type(self):
        
        # Resolve string references
        if isinstance(self.__type, basestring):
            self.__type = import_object(self.__type)
        
        return self.__type

    def _set_type(self, type):
        self.__type = type

    type = property(_get_type, _set_type, doc =
        """Imposes a data type constraint on the member. All values assigned to
        this member must be instances of the specified data type. Breaking this
        restriction will produce a validation error of type
        `exceptions.TypeCheckError`.
        
        The value for this constraint can take either a reference to a type
        object or a fully qualified python name. When set using a name, the
        indicated type will be imported lazily, the first time the value for
        this constraint is requested. This can be helpful in avoiding circular
        references between schemas.
        """)

    def _set_exclusive(self, expr):
        self.required = expr
        
        if isinstance(expr, Expression):        
            self.require_none = expr.not_()
        else:
            self.require_none = lambda ctx: not expr(ctx)

    exclusive = property(None, _set_exclusive, doc =
        """A write only property that eases the definition of members that
        should be required or empty depending on a condition and its negation,
        respectively.

        Should be set to a dynamic expression (a callable object, or an
        instance of `expressions.Expression`).
        """)

    def produce_default(self, instance = None):
        """Generates a default value for the member. Can be overridden (ie. to
        produce dynamic default values).

        :param instance: The instance that the default is produced for.

        :return: The resulting default value.
        """
        if instance is not None and self.name:
            default = getattr(instance, "default_" + self.name, self.default)
        else:
            default = self.default

        if isinstance(default, DynamicDefault):
            return default()
        else:
            return default

    def copy(self):
        """Creates a deep, unbound copy of the member."""
        return deepcopy(self)
    
    def __deepcopy__(self, memo):

        if self._copy_class:
            copy = self._copy_class()
        else:
            copy = self.__class__()

        memo[id(self)] = copy

        for key, value in self.__dict__.iteritems():
            if key not in self._special_copy_keys:
                copy.__dict__[key] = deepcopy(value, memo)
        
        copy._validations = list(self._validations)
        memo[id(self._validations)] = copy._validations
        
        copy._validations_wrapper = ListWrapper(copy._validations)
        memo[id(copy._validations_wrapper)] = copy._validations_wrapper

        copy.copy_source = self

        return copy

    def add_validation(self, validation):
        """Adds a validation function to the member.
        
        :param validation: A callable that will be added as a validation rule
            for the member. Takes two positional parameters (a reference to the
            member itself, and the value assigned to the member), plus any
            additional number of keyword arguments used to refine validation
            options and context. The callable should produce a sequence of
            `exceptions.ValidationError` instances.
        :type validation: callable

        :return: The validation rule, as provided.
        :rtype: callable
        """
        self._validations.append(validation)
        return validation
    
    def remove_validation(self, validation):
        """Removes one of the validation rules previously added to a member.

        :param validation: The validation to remove, as previously passed to
            `add_validation`.
        :type validation: callable

        :raise ValueError: Raised if the member doesn't have the indicated
            validation.
        """
        self._validations.remove(validation)

    def validations(self, recursive = True):
        """Iterates over all the validation rules that apply to the member.

        :param recursive: Indicates if the produced set of validations should
            include those declared on members contained within the member. This
            parameter is only meaningful on compound members, but is made
            available globally in order to allow the method to be called
            polymorphically using a consistent signature.
        :type recursive: bool

        :return: The sequence of validation rules for the member.
        :rtype: callable iterable
        """
        return self._validations_wrapper

    def validate(self, value, context = None, **context_params):
        """Indicates if the given value fulfills all the validation rules
        imposed by the member.
        
        :param value: The value to validate.
        
        :param context: Additional parameters used to fine tune the validation
            process.
        :type context: `ValidationContext`

        :param context_params: Arbitrary keyword parameters to feed the
            validation context with.
        """
        for error in self.get_errors(value, context, **context_params):
            return False

        return True
 
    def get_errors(self, value, context = None, **context_params):
        """Tests the given value with all the validation rules declared by the
        member, iterating over the resulting set of errors.

        :param value: The value to evaluate.

        :param context: Additional parameters used to fine tune the validation
            process.
        :type context: `ValidationContext`

        :param context_params: Arbitrary keyword parameters to feed the
            validation context with.

        :return: An iterable sequence of validation errors.
        :rtype: `exceptions.ValidationError` iterable
        """
        if context is None:
            context = ValidationContext(self, value, **context_params)

        for validation in self.validations():
            for error in validation(self, value, context):
                yield error

    @classmethod
    def resolve_constraint(cls, expr, context):
        """Resolves a constraint expression for the given context.
        
        Most constraints can be specified using dynamic expressions instead of
        static values, allowing them to adapt to different validation contexts.
        For example, a field may state that it should be required only if
        another field is set to a certain value. This method normalizes any
        constraint (either static or dynamic) to a static value, given a
        certain validation context.

        Dynamic expressions are formed by assigning a callable object or an
        `expressions.Expression` instance to a constraint value.

        :param expr: The constraint expression to resolve.
        
        :param context: The validation context that will be made available to
            dynamic constraint expressions.
        :type context: `ValidationContext`

        :return: The normalized expression value.
        """
        if not isinstance(expr, type):
            if isinstance(expr, Expression):
                validable = context.validable
                return expr.eval(validable, get_accessor(validable))
            elif callable(expr):
                return expr(context)
        
        return expr

    def member_validation_rule(self, value, context):
        """The base validation rule for all members. Tests the `required`,
        `require_none`, `enumeration` and `type` constraints.
        """
        # Value required
        if value is None:
            if self.resolve_constraint(self.required, context):
                yield exceptions.ValueRequiredError(self, value, context)

        # None required
        elif self.resolve_constraint(self.require_none, context):
            yield exceptions.NoneRequiredError(self, value, context)

        else:
            # Enumeration
            enumeration = self.resolve_constraint(self.enumeration, context)
            
            if enumeration is not None and value not in enumeration:
                yield exceptions.EnumerationError(
                    self, value, context, enumeration)

            # Type check
            type = self.resolve_constraint(self.type, context)

            if type and not isinstance(value, type):
                yield exceptions.TypeCheckError(self, value, context, type)

    def __translate__(self, language, qualified = False, **kwargs):
        if qualified and self.schema:
            return translations("cocktail.schema.Member qualified",
                member = self,
                language = language,
                **kwargs
            )
        else:
            return translations(
                self.schema.name + "." + self.name,
                language,
                chain = self.copy_source,
                **kwargs
            )

    def translate_value(self, value, language = None, **kwargs):
        if value is None:
            return u""
        else:
            return unicode(value)

    def get_member_explanation(self, language = None, **kwargs):
        
        explanation = None

        if self.schema and self.schema.name:        
            explanation = translations(
                self.schema.name + "." + self.name + "-explanation",
                language,
                **kwargs
            )

        if not explanation and self.copy_source:
            explanation = self.copy_source.get_member_explanation(
                language,
                **kwargs
            )

        return explanation


class DynamicDefault(object):

    def __init__(self, factory):
        self.factory = factory

    def __call__(self):
        return self.factory()

