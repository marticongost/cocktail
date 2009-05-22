#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from unittest import TestCase


class EventTestCase(TestCase):
    
    def test_instance(self):
        
        from cocktail.events import Event, EventInfo

        class Foo(object):
            spammed = Event()

        foo = Foo()

        # Make sure event slots get cached
        self.assertTrue(foo.spammed is foo.spammed)
        
        def test_event_info(event):
            self.assertEqual(event.target, foo)
            self.assertEqual(event.source, foo)
            self.assertEqual(event.x, 1)
            self.assertEqual(event.y, 2)
            self.assertEqual(event.slot, foo.spammed)

        def first_callback(event):
            test_event_info(event)
            event.executed.append(first_callback)

        def second_callback(event):
            test_event_info(event)
            event.executed.append(second_callback)

        foo.spammed.append(first_callback)
        self.assertEqual(len(foo.spammed), 1)
        self.assertTrue(foo.spammed[0] is first_callback)

        foo.spammed.append(second_callback)
        self.assertEqual(len(foo.spammed), 2)
        self.assertTrue(foo.spammed[0] is first_callback)
        self.assertTrue(foo.spammed[1] is second_callback)

        event_info = foo.spammed(x = 1, y = 2, executed = [])
        self.assertTrue(isinstance(event_info, EventInfo))
        
        for i in range(2):
            self.assertEqual(
                event_info.executed, [first_callback, second_callback]
            )

        foo.spammed.remove(first_callback)

        self.assertEqual(len(foo.spammed), 1)
        self.assertTrue(foo.spammed[0] is second_callback)

        event_info = foo.spammed(x = 1, y = 2, executed = [])
        self.assertTrue(isinstance(event_info, EventInfo))

        for i in range(2):
            self.assertEqual(event_info.executed, [second_callback])

    def test_class(self):
        
        from cocktail.events import Event, EventInfo

        class Foo(object):
            spammed = Event()

        # Make sure event slots get cached
        self.assertTrue(Foo.spammed is Foo.spammed)
        
        def test_event_info(event):
            self.assertEqual(event.target, Foo)
            self.assertEqual(event.source, Foo)
            self.assertEqual(event.x, 1)
            self.assertEqual(event.y, 2)
            self.assertEqual(event.slot, Foo.spammed)

        def first_callback(event):
            test_event_info(event)
            event.executed.append(first_callback)

        def second_callback(event):
            test_event_info(event)
            event.executed.append(second_callback)

        Foo.spammed.append(first_callback)
        self.assertEqual(len(Foo.spammed), 1)
        self.assertTrue(Foo.spammed[0] is first_callback)

        Foo.spammed.append(second_callback)
        self.assertEqual(len(Foo.spammed), 2)
        self.assertTrue(Foo.spammed[0] is first_callback)
        self.assertTrue(Foo.spammed[1] is second_callback)

        event_info = Foo.spammed(x = 1, y = 2, executed = [])
        self.assertTrue(isinstance(event_info, EventInfo))
        
        for i in range(2):
            self.assertEqual(
                event_info.executed, [first_callback, second_callback]
            )

        Foo.spammed.remove(first_callback)

        self.assertEqual(len(Foo.spammed), 1)
        self.assertTrue(Foo.spammed[0] is second_callback)

        event_info = Foo.spammed(x = 1, y = 2, executed = [])
        self.assertTrue(isinstance(event_info, EventInfo))

        for i in range(2):
            self.assertEqual(event_info.executed, [second_callback])

    def test_inheritance(self):
        
        from cocktail.events import Event, EventInfo

        class Foo(object):
            spammed = Event()
            
        class Bar(Foo):
            pass

        # Make sure event slots get cached
        self.assertTrue(Foo.spammed is Foo.spammed)
        self.assertTrue(Bar.spammed is Bar.spammed)
        self.assertTrue(Foo.spammed is not Bar.spammed)
        
        def test_base_event_info(event):
            self.assertEqual(event.target, Foo)
            self.assertEqual(event.source, event.tested_class)
            self.assertEqual(event.x, 1)
            self.assertEqual(event.y, 2)
            self.assertEqual(event.slot, Foo.spammed)

        def first_base_callback(event):
            test_base_event_info(event)
            event.executed.append(first_base_callback)

        def second_base_callback(event):
            test_base_event_info(event)
            event.executed.append(second_base_callback)

        def test_derived_event_info(event):
            self.assertEqual(event.target, Bar)
            self.assertEqual(event.source, event.tested_class)
            self.assertEqual(event.x, 1)
            self.assertEqual(event.y, 2)
            self.assertEqual(event.slot, Bar.spammed)

        def first_derived_callback(event):
            test_derived_event_info(event)
            event.executed.append(first_derived_callback)

        def second_derived_callback(event):
            test_derived_event_info(event)
            event.executed.append(second_derived_callback)

        Foo.spammed.append(first_base_callback)
        Foo.spammed.append(second_base_callback)

        Bar.spammed.append(first_derived_callback)
        Bar.spammed.append(second_derived_callback)
        
        event_info = Foo.spammed(
            x = 1, y = 2, tested_class = Foo, executed = [])
        
        for i in range(2):
            self.assertEqual(
                event_info.executed,
                [first_base_callback, second_base_callback]
            )

        event_info = Bar.spammed(
            x = 1, y = 2, tested_class = Bar, executed = [])
        
        for i in range(2):
            self.assertEqual(
                event_info.executed,
                [first_derived_callback,
                 second_derived_callback,
                 first_base_callback,
                 second_base_callback]
            )

    def test_instance_and_class(self):
        
        from cocktail.events import Event, EventInfo

        class Foo(object):
            spammed = Event()

        foo = Foo()

        # Make sure event slots get cached
        self.assertTrue(foo.spammed is foo.spammed)
        self.assertTrue(Foo.spammed is Foo.spammed)
        self.assertTrue(Foo.spammed is not foo.spammed)

        # Add instance callbacks
        def test_instance_event_info(event):
            self.assertEqual(event.target, foo)
            self.assertEqual(event.source, foo)
            self.assertEqual(event.x, 1)
            self.assertEqual(event.y, 2)
            self.assertEqual(event.slot, foo.spammed)

        def first_instance_callback(event):
            test_instance_event_info(event)
            event.test_string = "first instance callback"
            event.executed.append(first_instance_callback)

        def second_instance_callback(event):
            test_instance_event_info(event)
            event.test_string = "second instance callback"
            event.executed.append(second_instance_callback)

        foo.spammed.append(first_instance_callback)
        self.assertEqual(len(foo.spammed), 1)
        self.assertTrue(foo.spammed[0] is first_instance_callback)

        foo.spammed.append(second_instance_callback)
        self.assertEqual(len(foo.spammed), 2)
        self.assertTrue(foo.spammed[0] is first_instance_callback)
        self.assertTrue(foo.spammed[1] is second_instance_callback)

        # Add class-wide callbacks
        def test_class_event_info(event):
            self.assertEqual(event.target, Foo)
            self.assertEqual(event.source, foo)
            self.assertEqual(event.x, 1)
            self.assertEqual(event.y, 2)
            self.assertEqual(event.slot, Foo.spammed)

        def first_class_callback(event):
            test_class_event_info(event)
            event.test_string = "first class callback"
            event.executed.append(first_class_callback)

        def second_class_callback(event):
            test_class_event_info(event)
            event.test_string = "second class callback"
            event.executed.append(second_class_callback)

        Foo.spammed.append(first_class_callback)
        self.assertEqual(len(Foo.spammed), 1)
        self.assertTrue(Foo.spammed[0] is first_class_callback)

        Foo.spammed.append(second_class_callback)
        self.assertEqual(len(Foo.spammed), 2)
        self.assertTrue(Foo.spammed[0] is first_class_callback)
        self.assertTrue(Foo.spammed[1] is second_class_callback)

        # Trigger the event
        event_info = foo.spammed(x = 1, y = 2, executed = [])
        self.assertTrue(isinstance(event_info, EventInfo))
        
        for i in range(2):
            self.assertEqual(
                event_info.executed,
                [first_instance_callback, second_instance_callback,
                 first_class_callback, second_class_callback]
            )

        foo.spammed.remove(first_instance_callback)
        Foo.spammed.remove(first_class_callback)

        self.assertEqual(len(foo.spammed), 1)
        self.assertTrue(foo.spammed[0] is second_instance_callback)

        self.assertEqual(len(Foo.spammed), 1)
        self.assertTrue(Foo.spammed[0] is second_class_callback)

        event_info = foo.spammed(x = 1, y = 2, executed = [])
        self.assertTrue(isinstance(event_info, EventInfo))

        for i in range(2):
            self.assertEqual(
                event_info.executed,
                [second_instance_callback, second_class_callback]
            )
            self.assertEqual(
                event_info.test_string, "second class callback"
            )

    def test_instance_with_inheritance(self):
        
        from cocktail.events import Event

        class Foo(object):
            spammed = Event()
            
        class Bar(Foo):
            pass

        foo = Bar()
        
        def base_callback(event):
            self.assertTrue(event.target is Foo)
            self.assertTrue(event.source is foo)
            event.executed.append(base_callback)

        def derived_callback(event):
            self.assertTrue(event.target is Bar)
            self.assertTrue(event.source is foo)
            event.executed.append(derived_callback)

        def instance_callback(event):
            self.assertTrue(event.target is foo)
            self.assertTrue(event.source is foo)
            event.executed.append(instance_callback)

        Foo.spammed.append(base_callback)
        Bar.spammed.append(derived_callback)
        foo.spammed.append(instance_callback)
        
        event_info = foo.spammed(executed = [])
        
        for i in range(2):
            self.assertEqual(
                event_info.executed,
                [instance_callback, derived_callback, base_callback]
            )

    def test_consumed(self):

        from cocktail.events import Event

        class Foo(object):
            spammed = Event()

        foo = Foo()
       
        def first_instance_callback(event):
            self.assertFalse(event.consumed)
            event.consumed = True
            event.executed.append(first_instance_callback)

        def second_instance_callback(event):
            event.executed.append(second_instance_callback)

        def first_class_callback(event):
            self.assertFalse(event.consumed)
            event.consumed = True
            event.executed.append(first_class_callback)

        def second_class_callback(event):
            event.executed.append(second_class_callback)

        foo.spammed.append(first_instance_callback)
        foo.spammed.append(second_instance_callback)
        Foo.spammed.append(first_class_callback)
        Foo.spammed.append(second_class_callback)

        event_info = foo.spammed(executed = [])
        self.assertEqual(
            event_info.executed,
            [first_instance_callback, first_class_callback]
        )

    def test_decorator(self):

        from cocktail.events import Event, when

        class Foo(object):
            spammed = Event()

        foo = Foo()

        @when(foo.spammed)
        def instance_callback(event):
            pass
        
        self.assertEqual(len(foo.spammed), 1)
        self.assertTrue(foo.spammed[0] is instance_callback)

        @when(Foo.spammed)
        def class_callback(event):
            pass

        self.assertEqual(len(Foo.spammed), 1)
        self.assertTrue(Foo.spammed[0] is class_callback)

    def test_event_hub(self):

        from cocktail.events import Event, EventHub, event_handler

        class Foo(object):
            __metaclass__ = EventHub
            
            spammed = Event()

            @event_handler
            def handle_spammed(cls):
                pass
 
        self.assertEqual(list(Foo.spammed), [Foo.handle_spammed])
        
        class Bar(Foo):
            
            @event_handler
            def handle_spammed(cls):
                pass

        self.assertEqual(list(Bar.spammed), [Bar.handle_spammed])

