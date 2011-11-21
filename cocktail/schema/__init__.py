#-*- coding: utf-8 -*-
u"""
Provides classes to describe the structure, properties and meta data of Python
data types.
"""
from cocktail.schema.member import (
    Member,
    DynamicDefault
)
from cocktail.schema.schema import Schema
from cocktail.schema.rangedmember import RangedMember
from cocktail.schema.schematuples import Tuple
from cocktail.schema.schemacollections import (
    Collection, add, remove,
    RelationCollection,
    RelationList,
    RelationSet,
    RelationOrderedSet
)
from cocktail.schema.schemamappings import (
    Mapping,
    RelationMapping
)
from cocktail.schema.schemarelations import RelationMember
from cocktail.schema.schemareference import Reference
from cocktail.schema.schemastrings import String
from cocktail.schema.schemanumbers import (
    Number,
    Integer,
    Decimal,
    Float
)
try:
    from cocktail.schema.schemanumbers import Fraction
except ImportError:
    pass
from cocktail.schema.schemabooleans import Boolean
from cocktail.schema.schemadates import (
    BaseDateTime,
    DateTime,
    Date,
    Time
)
from cocktail.schema.url import URL
from cocktail.schema.emailaddress import EmailAddress
from cocktail.schema.phonenumber import PhoneNumber
from cocktail.schema.color import Color
from cocktail.schema.creditcardnumber import CreditCardNumber
from cocktail.schema.codeblock import CodeBlock
from cocktail.schema.errorlist import ErrorList
from cocktail.schema.accessors import (
    get_accessor,
    get,
    set,
    MemberAccessor,
    AttributeAccessor,
    DictAccessor
)
from cocktail.schema.schemaobject import (
    SchemaObject,
    SchemaClass,
    SchemaObjectAccessor,
    TranslationMapping
)
from cocktail.schema.adapter import (
    reference, shallow, deep,
    Adapter,
    RuleSet,
    Rule,
    Copy,
    Exclusion,
    Split,
    Join
)
from cocktail.schema.validationcontext import ValidationContext
from cocktail.schema.differences import diff

