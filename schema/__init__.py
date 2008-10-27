#-*- coding: utf-8 -*-
"""
Declarative definition of data models and validation rules.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail.schema.member import Member, DynamicDefault
from cocktail.schema.schema import Schema
from cocktail.schema.rangedmember import RangedMember
from cocktail.schema.schemacollections import Collection
from cocktail.schema.schemamappings import Mapping
from cocktail.schema.schemareference import Reference
from cocktail.schema.schemastrings import String
from cocktail.schema.schemanumbers import Number, Integer, Decimal, Float
from cocktail.schema.schemabooleans import Boolean
from cocktail.schema.schemadates import BaseDateTime, DateTime, Date, Time
from cocktail.schema.errorlist import ErrorList
from cocktail.schema.accessors import (
    get_accessor,
    get,
    set,
    MemberAccessor,
    AttributeAccessor,
    DictAccessor
)
from cocktail.schema.adapter import (    
    Adapter, RuleSet,
    reference, shallow, deep,
    Rule, Copy, Exclusion, Split, Join,
)
