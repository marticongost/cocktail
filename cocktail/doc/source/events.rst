=========================================================================
`cocktail.events` -- Declaration, subscription and notification of events
=========================================================================

.. module:: cocktail.events
    :synopsis: An event mechanism for python.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>

The `cocktail.events` module provides the necessary constructions to declare,
listen to and trigger object events. Each *event* represents a certain
condition or state transition that may be of interest to other code. When met,
these conditions issue a notification, so that subscribers to that event can
be aware of the change.

.. _declaration:

Event declaration
-----------------
Classes declare `event <Event>` objects for each kind of condition that they
want to publicize.

For example, the following snippet declares three different events on a class::
    
    class Letter(object):
        written = Event()
        sending = Event()
        received = Event()

This will allow instances of the *Letter* class to notify other code when they
are written, about to be sent or received.

The `Event` constructor also supports an optional parameter, containing the
event's docstring::

    class Letter(object):
        written = Event(
            """An event triggered when the letter has been written."""
        )

.. _callback-registration:

Registration of event callbacks
-------------------------------
Events allow third party code to extend the behavior of an object, by
registering callback functions that will be invoked when the event
:ref:`is triggered <triggering>` on it.

.. _basic-registration:

Basic callback registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Callback functions are registered in `event slots <EventSlot>`, which are
produced by instances of the `Event` class on demand to keep track of the
callbacks registered to each object. Event slots behave mostly like standard
Python lists, which means that appending, inserting or removing a callback from
the slot is possible, using the typical API for lists.

Keeping with the *Letter* example, the following snippet adds a callback that
will print a message whenever a certain letter is about to be sent::

    def print_message(e):
        print "Sending a letter"

    my_letter.sending.append(print_message)

.. _event-information:

Event information
~~~~~~~~~~~~~~~~~
Callback functions must receive a single parameter: an instance of the
`EventInfo` class, which will contain relevant information about the event that
invoked the callback.

The data provided by `EventInfo` objects will typically be a mixture of event
:ref:`specific parameters <event-parameters>`, plus a set of standard
attributes.

To exemplify the use of the `EventInfo` object, here's how the previous example
could use the standard `~EventInfo.source` attribute to obtain a reference to
the letter for which the callback is being invoked::

    def print_message(e):        
        print "Sending letter %s to %s" % (e.source.title, e.source.receiver)

    my_letter.sending.append(print_message)

.. _multiple-callbacks:

Registering multiple callbacks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each `event slot <EventSlot>` can register an arbitrary number of callbacks.
This allows extending an object from multiple points, without the fear of
overwriting the changes introduced by another party.

When an event is triggered, its callbacks will be executed in the same order
in which they appear in the slot.

The following snippet extends the previous example by registering a second
callback::

    def print_message(e):
        print "Sending letter %s to %s" % (e.source.title, e.source.receiver)
    
    def blacklist_receivers(e):
        if is_blacklisted(e.source.receiver):
            raise ValueError(
                "Sending messages to %s is not enabled"
                % e.source.receiver
            )

    my_letter.sending.append(print_message)
    my_letter.sending.append(blacklist_receivers)

When the *sending* event is triggered on the letter, the blacklist check will
be executed after the message is printed.

.. _class-callbacks:

Registering class callbacks
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Callbacks can also be registered on a per class basis: accessing an event on a
class yields an `event slot <EventSlot>` bound to that class. Any callback that
is added to that slot will apply to any instance of the class (or of any of its
subclasses).

In the following example, *print_message* will apply to both instances of the
*Letter* class, but *print_importance_warning* will only affect *letter2*::

    def print_message(e):
        print "Sending a letter"

    def print_importance_warning(e):
        print "Sending a very important letter!"

    letter1 = Letter()
    letter2 = Letter()

    Letter.sending.append(print_message)
    letter2.sending.append(print_importance_warning)

.. _alternative-registration-syntax:

Alternative registration syntax
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following constructs can make the registration of event callbacks a bit
more convenient.

.. _when-decorator:

Using the `when` decorator
++++++++++++++++++++++++++
The `when` decorator makes the code for registering callbacks slightly more
clean and compact. It works like this::

    @when(my_letter.received)
    def print_message(e):
        print "Letter %s has been received by %s" % (e.source.title, e.source.receiver)

.. _event-hub:

Using the `EventHub` metaclass
++++++++++++++++++++++++++++++
A very common need that can arise when subclassing a type that exposes an event
is to register a callback for the subclass. One can do this the usual way::

    class BaseClass(object):
        base_event = Event()

    class DerivedClass(BaseClass):
        pass

    def derived_class_handler_for_base_event(e):
        pass

    DerivedClass.base_event.append(derived_class_handler_for_base_event)

But this is rather verbose, and moves logic that should belong to the class
outside of its definition.

To solve this issues, the module supplies an `EventHub` metaclass and an
`event_handler` decorator. Any class that uses this metaclass will
automatically register any of its methods marked with the `event_handler`
decorator as class level event callbacks. A naming convention is used to match
the methods with their target event: method names must consist of the *handle_*
prefix, followed by the name of the event that the callback should be
registered to.

This is how the last example would look like using this alternative form::

    class BaseClass(object):
        __metaclass__ = EventHub
        base_event = Event()

    class DerivedClass(BaseClass):

        @event_handler
        def handle_base_event(cls, e):
            pass

.. _triggering:

Triggering events
-----------------
An event is triggered by accessing one of its slots and calling it, just like
if it were a function. Triggering an event will execute all its previously
registered callbacks.

For example, to indicate to a letter that it is about to be sent, one would
simply do::

    letter.sending()

.. _event-parameters:

Passing event parameters
~~~~~~~~~~~~~~~~~~~~~~~~
When triggering an event, it is very often necessary to pass contextual
information to its registered callbacks. To address this need, slots can be
called with arbitrary keyword parameters, which will be made available as
attributes of the `EventInfo` object that will be passed to callbacks.

Here's an example::

    @when(button.clicked)
    def print_coordinates(e):
        print "Button %s clicked at position (%d,%d)" % (e.source, e.x, e.y)

    button.clicked(x = 45, y = 73)

Also, note that when an event is triggered, only one `EventInfo` object is
created, and it will be shared by all callbacks invoked by the event. This can
be used to convey state between callbacks, or to return data to the code that
triggered the event.

.. _callback-execution-order:

Callback execution order
~~~~~~~~~~~~~~~~~~~~~~~~
Since class level callbacks and class inheritance make it possible for more
than one slot to intervene in the invocation of an event, it can be important
to know the order in which these slots will be invoked.

* The callbacks in the slot that triggers the event are always executed first
* If it is an object slot, the slots for its classes are executed next,
  following Python's method resolution order
* If it is a class slot, the slots for its base classes are executed next,
  following Python's method resolution order

This procedure is applied recursively, until all slots have been executed. As
the event bubbles up, the `~EventInfo.target` and `~EventInfo.slot` attributes
of its `EventInfo` object will be updated to reflect the position in the chain,
but the `~EventInfo.source` attribute will remain constant.

.. _module-members:

Module members
--------------
Here are the details on all the objects provided by the module:

.. autoclass:: Event
    :members:

.. autoclass:: EventSlot
    :members:

.. autoclass:: EventInfo
    :members:

.. autofunction:: when

.. autoclass:: EventHub

.. autoclass:: event_handler

