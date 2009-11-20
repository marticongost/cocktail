#-*- coding: utf-8 -*-
u"""
A set of constructs for modeling classes.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2007
"""
import types
from copy import copy, deepcopy
from threading import local, Lock, RLock
from cocktail.typemapping import TypeMapping

_thread_data = local()
_undefined = object()

def wrap(function, wrapper):
    wrapper.__doc__ = function.__doc__
    wrapper.func_name = function.func_name

def getter(function):
    return property(function, doc = function.__doc__)

def abstractmethod(func):
    
    def wrapper(self, *args, **kwargs):
        raise TypeError(
            "Calling abstract method %s on %s"
            % func.func_name, self
        )

    wrap(func, wrapper)
    return wrapper

class classgetter(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls = None):
        
        if cls is None and instance is not None:
            cls = type(instance)
           
        if cls is None:
            return self
        else:
            return self.func(cls)

class CustomProperty(property):
    pass

def cached_getter(function):
    """A method decorator used to define read-only cached properties. The value
    of the property will be computed the first time it is accessed, using the
    decorated method, and reused on all further calls.

    Each instance of the method's class will gain its own cached value.
    """ 
    undefined = object()
    key = "_" + function.func_name
    
    def wrapper(self):
        value = getattr(self, key, undefined)

        if value is undefined:
            value = function(self)
            setattr(self, key, value)

        return value

    class CachedGetter(property):
        def __call__(self, instance):
            return function(instance)

        def clear(self, instance):
            try:
                delattr(instance, key)
            except AttributeError:
                pass

    return CachedGetter(wrapper, doc = function.__doc__)

def refine(element):
    
    def decorator(function):

        def wrapper(*args, **kwargs):
            return function(element, *args, **kwargs)

        wrap(function, wrapper)
        setattr(element, function.func_name, wrapper)
        return wrapper

    return decorator

def call_base(*args, **kwargs):
    method_stack = getattr(_thread_data, "method_stack", None)
    if method_stack:
        return method_stack[-1](*args, **kwargs)

def extend(element):

    def decorator(function):

        base = getattr(element, function.func_name, None)

        if base:
            def wrapper(*args, **kwargs):
                if not hasattr(_thread_data, "method_stack"):
                    _thread_data.method_stack = []
                try:
                    _thread_data.method_stack.append(base)
                    rvalue = function(element, *args, **kwargs)

                    if isinstance(rvalue, types.GeneratorType):
                        raise TypeError(
                            "extend() doesn't work with generator functions "
                            "(calling %s on %s)" % (function, element))

                    return rvalue
                finally:
                    _thread_data.method_stack.pop()

            wrap(function, wrapper)
            wrapper.im_self = element
            setattr(element, function.func_name, wrapper)
        else:
            def wrapper(*args, **kwargs):
                return function(element, *args, **kwargs)
            wrapper.func_name = function.func_name
            wrapper.im_self = element
        
        setattr(element, function.func_name, wrapper)
        return wrapper

    return decorator


class GenericMethod(object):

    def __init__(self, default):
        self.default = default
        self.implementations = TypeMapping()

    def __call__(self, instance, *args, **kwargs):
        impl = self.implementations.get(instance.__class__, self.default)
        return impl(instance, *args, **kwargs)


# Read-only collection wrappers
#------------------------------------------------------------------------------ 

class DictWrapper(object):

    def __init__(self, items = None):
        if items is None:
            items = {}
        self._items = items

    def __copy__(self):
        return copy(self._items)

    def __deepcopy__(self, memo):
        return deepcopy(self._items, memo)

    def __contains__(self, key):
        return self._items.__contains__(key)

    def __eq__(self, other):
        if isinstance(other, DictWrapper):
            other = other._items        
        return self._items == other

    def __ge__(self, other):
        if isinstance(other, DictWrapper):
            other = other._items
        return self._items >= other

    def __getitem__(self, key):
        return self._items.__getitem__(key)

    def __gt__(self, other):
        if isinstance(other, DictWrapper):
            other = other._items
        return self._items > other

    def __hash__(self):
        return self._items.__hash__()

    def __iter__(self):
        try:
            return self._items.__iter__()
        except AttributeError:
            return (item for item in self._items)

    def __le__(self, other):
        if isinstance(other, DictWrapper):
            other = other._items
        return self._items < other

    def __len__(self):
        return self._items.__len__()

    def __lt__(self, other):
        if isinstance(other, DictWrapper):
            other = other._items
        return self._items.__lt__(other)

    def __ne__(self, other):
        if isinstance(other, DictWrapper):
            other = other._items
        return self._items != other

    def __repr__(self):
        return self._items.__repr__()

    def __str__(self):
        return self._items.__str__()

    def copy(self):
        return self._items.copy()

    def get(self, key, default = None):
        return self._items.get(key, default)

    def has_key(self, key):
        return self._items.has_key(key)

    def items(self):
        return self._items.items()

    def iteritems(self):
        return self._items.iteritems()

    def iterkeys(self):
        return self._items.iterkeys()
    
    def itervalues(self):
        return self._items.itervalues()

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

class ListWrapper(object):

    def __init__(self, items = None):
        if items is None:
            items = []
        self._items = items

    def __copy__(self):
        return copy(self._items)

    def __deepcopy__(self, memo):
        return deepcopy(self._items, memo)

    def __add__(self, other):
        return self._items.__add__(other)

    def __contains__(self, item):
        return self._items.__contains__(item)
    
    def __eq__(self, other):
        if isinstance(other, ListWrapper):
            other = other._items
        return self._items == other

    def __ge__(self, other):
        if isinstance(other, ListWrapper):
            other = other._items        
        return self._items >= other

    def __getitem__(self, index):
        return self._items.__getitem__(index)

    def __getslice__(self, i, j):
        return self._items.__getslice__(i, j)

    def __gt__(self, other):        
        if isinstance(other, ListWrapper):
            other = other._items        
        return self._items > other

    def __hash__(self):
        return self._items.__hash__()

    def __iter__(self):
        try:
            return self._items.__iter__()
        except AttributeError:
            return (item for item in self._items)

    def __le__(self, other):
        if isinstance(other, ListWrapper):
            other = other._items        
        return self._items <= other

    def __len__(self):
        return self._items.__len__()

    def __lt__(self, other):
        if isinstance(other, ListWrapper):
            other = other._items
        return self._items < other

    def __mul__(self, other):
        return self._items.__mul__(other)

    def __ne__(self, other):
        if isinstance(other, ListWrapper):
            other = other._items
        return self._items != other

#    def __reduce__(self):
#        return self._items.__reduce__()

#    def __reduce_ex__(self, protocol):
#        return self._items.__reduce_ex__(protocol)

    def __repr__(self):
        return self._items.__repr__()

    def __reversed__(self):
        return self._items.__reversed__()

    def __rmul__(self, other):
        return self._items.__rmul__(other)

    def __str__(self):
        return self._items.__str__()

    def count(self, item):
        return self._items.count(item)

    def index(self, item):
        return self._items.index(item)

class SetWrapper(object):

    def __init__(self, items = None):
        if items is None:
            items = set()
        self._items = items

    def __copy__(self):
        return copy(self._items)

    def __deepcopy__(self, memo):
        return deepcopy(self._items, memo)

    def __and__(self, other):
        return self._items.__and__(other)

    def __contains__(self, item):
        return self._items.__contains__(item)

    def __eq__(self, other):
        if isinstance(other, SetWrapper):
            other = other._items
        return self._items == other

    def __ge__(self, other):
        if isinstance(other, SetWrapper):
            other = other._items
        return self._items >= other

    def __gt__(self, other):
        if isinstance(other, SetWrapper):
            other = other._items
        return self._items > other

    def __hash__(self):
        return self._items.__hash__()

    def __iter__(self):
        try:
            return self._items.__iter__()
        except AttributeError:
            return (item for item in self._items)

    def __le__(self, other):
        if isinstance(other, SetWrapper):
            other = other._items
        return self._items <= other

    def __len__(self):
        return self._items.__len__()

    def __lt__(self, other):
        if isinstance(other, SetWrapper):
            other = other._items
        return self._items < other

    def __ne__(self, other):
        if isinstance(other, SetWrapper):
            other = other._items
        return self._items != other

    def __or__(self, other):
        return self._items.__or__(other)

    def __rand__(self, other):
        return self._items.__rand__(other)

#    def __reduce__(self):
#        return self._items.__reduce__()

#    def __reduce_ex__(self, protocol):
#        return self._items.__reduce_ex__(protocol)

    def __repr__(self):
        return self._items.__repr__()

    def __ror__(self, other):
        return self._items.__ror__(other)

    def __rsub__(self, other):
        return self._items.__rsub__(other)

    def __rxor__(self, other):
        return self._items.__rxor__(other)

    def __sub__(self, other):
        return self._items.__sub__(other)

    def __xor__(self, other):
        return self._items.__xor__(other)

    def __str__(self):
        return self._items.__str__()

    def copy(self):
        return self._items.copy()

    def difference(self, other):
        return self._items.difference(other)
    
    def intersection(self, other):
        return self._items.intersection(other)

    def issubset(self, other):
        return self._items.issubset(other)

    def issuperset(self, other):
        return self._items.issuperset(other)

    def symmetric_difference(self, other):
        return self._items.symmetric_difference(other)

    def union(self, other):
        return self._items.union(other)

empty_dict = DictWrapper({})
empty_list = ListWrapper([])
empty_set = SetWrapper(set())


# Ordered collections
#------------------------------------------------------------------------------

class OrderedSet(ListWrapper):
    """An ordered set of items.
    
    Ordered sets behave mostly as lists without repetitions, and the API for
    both types is roughly the same.
    """
    
    def __init__(self, items = None):
        ListWrapper.__init__(self, [])
        if items:
            self.extend(items)

    def append(self, item, relocate = False):
        
        try:
            pos = self._items.index(item)
        except ValueError:
            self._items.append(item)
            return True            
        else:        
            if relocate:
                self._items.pop(pos)
                self._items.append(item)

            return False

    def insert(self, pos, item, relocate = False):

        try:
            prev_pos = self._items.index(item)
        except ValueError:
            self._items.insert(pos, item)
            return True
        else:
            if relocate:
                self._items.pop(prev_pos)
                self._items.insert(pos, item)
            
            return False

    def extend(self, items, relocate = False):
        for item in items:
            self.append(item, relocate)

    def pop(self, pos):
        self._items.pop(pos)

    def remove(self, item):
        self._items.remove(item)
 
    def reverse(self):
        self._items.reverse()

    def sort(self, *args):
        self._items.sort(*args)

    def __copy__(self):
        return self.__class__(copy(self._items))

    def __deepcopy__(self, memo):
        return self.__class__(deepcopy(self._items))

    def __setitem__(self, i, item):
        if item not in self._items:
            self._items[i] = item

    def __delitem__(self, i):
        self._items.__delitem__(i)

    def __setslice__(self, i, j, other):
        head = self._items[:i]
        tail = self._items[j:]
        self._items = \
            head + [x for x in other if x not in head and x not in tail] + tail
    
    def __delslice__(self, i, j):
        self._items.__delslice__(i, j)

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __imul__(self, n):
        raise TypeError("Operation not permitted")


class OrderedDict(DictWrapper):

    def __init__(self, *args, **kwargs):
        DictWrapper.__init__(self, {})
        self.__sequence = []
        self.update(*args, **kwargs)

    def __iter__(self):
        return self.__sequence.__iter__()

    def keys(self):
        return list(self.__sequence)

    def iterkeys(self):
        return self.__sequence.__iter__()

    def values(self):
        return [self._items[key] for key in self.__sequence]
    
    def itervalues(self):
        for key in self.__sequence:
            yield self._items[key]

    def items(self):
        return [(key, self._items[key]) for key in self.__sequence]
    
    def iteritems(self):
        for key in self.__sequence:
            yield (key, self._items[key])

    def __setitem__(self, key, value):
        if key not in self._items:
            self.__sequence.append(key)
        self._items[key] = value

    def __delitem__(self, key):
        self._items.__delitem__(key)
        self.__sequence.remove(key)
    
    def clear(self):
        self._items = {}
        self.__sequence = []

    def pop(self, key, default = _undefined):

        value = self._items.get(key, _undefined)

        if value is _undefined:
            if default is _undefined:
                raise KeyError(key)
            value = default
        else:
            del self[key]

        return value

    def popitem(self, index = -1):
        key = self.__sequence.pop(index)
        value = self._items.pop(key)
        return key, value

    def update(self, *args, **kwargs):
        if args:
            if len(args) != 1:
                raise TypeError(
                    "update expected at most 1 argument, got %d"
                    % len(args)
                )
            
            source = args[0]

            if isinstance(source, (dict, DictWrapper)):
                source = source.iteritems()

            for key, value in source:
                self[key] = value

        if kwargs:
            for key, value in kwargs.iteritems():
                self[key] = value


# Instrumented collections
#------------------------------------------------------------------------------ 

class InstrumentedCollection(object):
    
    def item_added(self, item):
        pass

    def item_removed(self, item):
        pass


class InstrumentedList(ListWrapper, InstrumentedCollection):

    def __init__(self, items = None):
        ListWrapper.__init__(self, items)

    def append(self, item):
        self._items.append(item)
        self.item_added(item)

    def insert(self, index, item):
        self._items.insert(index, item)
        self.item_added(item)

    def extend(self, items):
        self._items.extend(items)
        for item in items:
            self.item_added(item)

    def remove(self, item):
        self._items.remove(item)
        self.item_removed(item)
    
    def pop(self, index):
        item = self._items.pop(index)
        self.item_removed(item)
        return item

    def __setitem__(self, index, item):
                
        prev_item = self._items[index]

        if item != prev_item:
            self._items[index] = item
            self.item_removed(prev_item)
            self.item_added(item)

    def __delitem__(self, index):
        
        if isinstance(index, slice):
            items = self._items[index]
            self._items.__delitem__(index)
            for item in items:
                self.item_removed(item)
        else:
            item = self._items.pop(index)
            self.item_removed(item)


class InstrumentedOrderedSet(ListWrapper, InstrumentedCollection):

    def __init__(self, items = None):
        if items and not isinstance(items, OrderedSet):
            raise TypeError(
                "Ordered set expected, got %s instead" %
                items.__class__.__name__
            )
        ListWrapper.__init__(self, items or OrderedSet())

    def append(self, item, relocate = False):
        if self._items.append(item, relocate):
            self.item_added(item)

    def insert(self, index, item, relocate = False):
        if self._items.insert(index, item, relocate):
            self.item_added(item)

    def extend(self, items, relocate = False):
        for item in items:
            self.append(item, relocate)

    def remove(self, item):
        self._items.remove(item)
        self.item_removed(item)
    
    def pop(self, index):
        item = self._items.pop(index)
        self.item_removed(item)
        return item

    def __setitem__(self, index, item):
        
        if item not in self._items:
            prev_item = self._items[index]
            self._items[index] = item
            self.item_removed(prev_item)
            self.item_added(item)

    def __delitem__(self, index):
        
        if isinstance(index, slice):
            items = self._items[index]
            self._items.__delitem__(index)
            for item in items:
                self.item_removed(item)
        else:
            item = self._items.pop(index)
            self.item_removed(item)


class InstrumentedSet(SetWrapper, InstrumentedCollection):

    def __init__(self, items = None):
        SetWrapper.__init__(self, items)

    def add(self, item):
        if item not in self._items:
            self._items.add(item)
            self.item_added(item)

    def clear(self):
        items = list(self._items)
        self._items.clear()

        for item in items:
            self.item_removed(item)

    def difference_update(self, other_set):
        items = self._items & other_set
        self._items.difference_update(other_set)

        for item in items:
            self.item_removed(item)

    def discard(self, item):
        if item in self._items:
            self._items.remove(item)
            self.item_removed(item)

    def intersection_update(self, other_set):
        items = self._items - other_set
        self._items.intersection_update(other_set)

        for item in items:
            self.item_removed(item)

    def pop(self):
        item = self._items.pop()
        self.item_removed(item)
        return item

    def remove(self, item):
        self._items.remove(item)
        self.item_removed(item)
        
    def symmetric_difference_update(self, other_set):
        
        removed_items = self._items & other_set
        added_items = other_set - self._items
        self._items.difference_update(removed_items)
        self._items.update(added_items)        

        for item in removed_items:
            self.item_removed(item)

        for item in added_items:
            self.item_added(item)

    def update(self, other_set):
        items = other_set - self._items
        self._items.update(items)

        for item in items:
            self.item_added(item)


class InstrumentedDict(DictWrapper, InstrumentedCollection):

    def __init__(self, items = None):
        DictWrapper.__init__(self, items)

    def __setitem__(self, key, value):
        prev_value = self._items.get(key, _undefined)
        self._items.__setitem__(key, value)

        if value != prev_value:
            
            if prev_value is not _undefined:
                self.item_removed((key, prev_value))
            
            self.item_added((key, value))

    def __delitem__(self, key):
        value = self._items.pop(key)
        self.item_removed((key, value))

    def clear(self):
        items = self._items.items()
        self._items.clear()

        for item in items:
            self.item_removed(item)

    def pop(self, key, default = _undefined):

        value = self._items.get(key, _undefined)

        if value is _undefined:
            if default is _undefined:
                raise KeyError(key)
            value = default
        else:
            del self._items[key]
            self.item_removed((key, value))

        return value

    def popitem(self):
        item = self._items.popitem()
        self.item_removed(item)
        return item

    def update(self, *args, **kwargs):
        if args:
            if len(args) != 1:
                raise TypeError(
                    "update expected at most 1 argument, got %d"
                    % len(args)
                )
        
            for key, value in args[0].iteritems():
                self[key] = value

        if kwargs:
            for key, value in kwargs.iteritems():
                self[key] = value
 

# Thread safe collections
#------------------------------------------------------------------------------ 

class SynchronizedList(object):

    _list_class = list
    _lock_class = RLock

    def __init__(self, items = None):
        
        if items is None:
            items = self._list_class()
        elif not isinstance(items, self._list_class):
            items = self._list_class(items)

        self._items = items
        self.lock = self._lock_class()
        
        # FIXME: This is a nasty hack, but its the only apparent way to turn
        # off the nasty mandatory on-screen debugging imposed by
        # threading.RLock
        self.lock._note = lambda *args: None

    def __copy__(self):
        self.lock.acquire()
        try:
            return self._items.__copy__(self)
        finally:
            self.lock.release()

    def __deepcopy__(self, memo):
        self.lock.acquire()
        try:
            return self._items.__deepcopy__(memo)
        finally:
            self.lock.release()

    def __add__(self, other):
        return self._items.__add__(other)
        
    def __contains__(self, item):
        return self._items.__contains__(item)
            
    def __eq__(self, other):
        return self._items.__eq__(other)
        
    def __ge__(self, other):
        return self._items.__ge__(other)
        
    def __getitem__(self, index):
        return self._items.__getitem__(index)
        
    def __getslice__(self, i, j):
        return self._items.__getslice__(i, j)
        
    def __gt__(self, other):
        return self._items.__gt__(other)
        
    def __hash__(self):
        return self._items.__hash__()
        
    def __iter__(self):
        self.lock.acquire()
        try:
            return list(self._items).__iter__()
        finally:
            self.lock.release()

    def __le__(self, other):
        return self._items.__le__(other)
        
    def __len__(self):
        return self._items.__len__()
        
    def __lt__(self, other):
        return self._items.__lt__(other)
        
    def __mul__(self, other):
        return self._items.__mul__(other)
        
    def __ne__(self, other):
        return self._items.__ne__(other)
        
    def __repr__(self):
        return self._items.__repr__()
        
    def __reversed__(self):
        self.lock.acquire()
        try:
            items = list(self._items)
            items.reverse()
            return items
        finally:
            self.lock.release()

    def __rmul__(self, other):
        return self._items.__rmul__(other)
        
    def __str__(self):
        return self._items.__str__()
        
    def count(self, item):
        return self._items.count(item)
        
    def index(self, item):
        return self._items.index(item)
        
    def append(self, item):
        self._items.append(item)
        
    def insert(self, index, item):
        self._items.insert(index, item)        

    def extend(self, items):
        self._items.extend(items)
        
    def remove(self, item):
        self._items.remove(item)
        
    def pop(self, index):
        return self._items.pop(index)
        
    def __setitem__(self, index, item):
        self._items[index] = item
        
    def __delitem__(self, index):
        self._items.__delitem__(index)


class ContextualDict(DictWrapper):

    def __init__(self):
        self.__local = local()

    @getter
    def _items(self):
        items = getattr(self.__local, "items", None)

        if items is None:
            items = {}
            self.__local.items = items

        return items

    def __setitem__(self, key, value):
        self._items[key] = value

    def __delitem__(self, key):
        del self._items[key]

    def clear(self):
        self._items.clear()
        
    def pop(self, *args):
        return self._items.pop(*args)

    def popitem(self):
        return self._items.popitem()

    def update(self, *args, **kwargs):
        return self._items.update(*args, **kwargs)

