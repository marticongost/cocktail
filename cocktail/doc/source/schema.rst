==========================================================
`cocktail.schema` -- Declarative description of data types
==========================================================

.. module:: cocktail.schema
    :synopsis: Describe the properties of data types.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>

The *schema* module provides classes to describe the structure, properties and
meta data of Python data types. The description of a unit of data typically
includes a combination of the following features:

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
  parameters from HTTP requests, or to generate web services for a data type

Members
-------

The center of the package lies in the `Member` class, which provides the
basic means to define a single piece of data. *Member* is inherited by a wealth
of other classes, that add the necessary features to describe a diversity of
concrete data types (`String`, `Integer`, `Boolean`, etc.).

Members can also be composited, in order to describe parts of a more complex
data set, by using `collections <Collection>` or `schemas <Schema>`.

.. autoclass:: Member
    :members:

Validation
~~~~~~~~~~
Blah blah

.. _dynamic-expressions:

Dynamic expressions
+++++++++++++++++++


.. _member-types:

Member types
~~~~~~~~~~~~

.. _string:

Strings
+++++++

.. _boolean:

Boolean
+++++++

.. _numbers:

Numbers
+++++++

.. _references:

References
++++++++++

.. _collection:

Collections
+++++++++++

.. _schemas:

Schemas
+++++++

Relations

