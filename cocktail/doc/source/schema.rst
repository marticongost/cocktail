==========================================================
`cocktail.schema` -- Declarative description of data types
==========================================================

.. automodule:: cocktail.schema
    :synopsis: Declarative description of data types

.. moduleauthor:: Martí Congost <marti.congost@whads.com>

The description of a unit of data typically includes a combination of the
following features:

* An statement about the type of Python values accepted by the described unit
* The set of constraints and validation rules the described unit must fulfill
* Any number of arbitrary meta data properties

Having access to this explicit description of a type's features encourages
introspective and declarative programming, and enables a series of interesting
effects. As an example, most other packages in the `cocktail` library make
extensive use of the functionality provided by this package:

* `cocktail.persistence` uses type descriptions to persist objects to a
  database
* `cocktail.html` is able to generate HTML forms, tables and other
  presentation elements from a schema definition
* `cocktail.controllers` takes advantage of type definitions to read
  parameters from HTTP requests, or to generate web services for data types

.. _describing-data-types:

Describing data types
---------------------
Each description of a specific unit of data is represented with an instance of
the `Member` class (or more typically, one of its
:ref:`subclasses <member-types>`). 

All members share a common set of capabilities:

* They can be given a `name`, to identify them uniquely in different contexts
* They can be used as stand alone objects, to describe discrete units of data,
  or embedded within a :ref:`collection <collections>` or
  :ref:`schema <schemas>`, to describe more complex data types
* They can be used to :ref:`validate <validation>` instances of the data they
  describe

.. _member-types:

Member types
~~~~~~~~~~~~
As noted, the `Member` class provides a base feature set, common to all kinds
of members, but it is seldom instantiated on its own. Instead, the package
provides an assortment of subclasses, each suited to describing instances of
different data types:

* `String` describes text values, and supports restricting the length and
  format of its values
* `Boolean` handles boolean (True/False) values
* `Integer`, `Decimal` and `Float` deal with numeric types, and can establish
  minimum and maximum allowed values
* `Date`, `Time` and `DateTime` represent date and time values. As well as
  setting a range of valid values, these members also act as :ref:`schemas`,
  combining a set of integer members that can be constrained and modified on
  their own (ie. "the year must be one of 1998, 1999 and 2000")
* `Reference` describes a pointer to an object

.. _collections:

Collections
~~~~~~~~~~~
`Collections <Collection>` allow describing sets of values, such as lists,
sets or tuples. They have constraints on the minimum and maximum length of
their
values

.. _schemas:

Schemas
~~~~~~~

.. _schema-object:

The `SchemaObject` class
~~~~~~~~~~~~~~~~~~~~~~~~

.. _validation:

Validation
----------

.. _validation-context:

The validation context
~~~~~~~~~~~~~~~~~~~~~~

.. _validating-objects:

Validating objects
~~~~~~~~~~~~~~~~~~

.. _dynamic-constraints:

Dynamic constraints
~~~~~~~~~~~~~~~~~~~

.. _writing-validation-rules:

Writing validation rules
~~~~~~~~~~~~~~~~~~~~~~~~

.. _value-accessors:

Value accessors
---------------

.. _adaptation:

Adaptation
----------

.. _module-contents:

Module contents
---------------

