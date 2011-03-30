#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
import cherrypy
from cocktail.modeling import DictWrapper

undefined = object()


class Session(DictWrapper):

    config = {
        'session.type': 'memory',
        'session.cookie_expires': True,
        'session.timeout': 3600
    }

    def __init__(self):
        pass

    @property
    def _items(self):
        return cherrypy.request.wsgi_environ['beaker.session']
    
    def __setitem__(self, key, value):
        self.save()
        self._items[key] = value

    def __delitem__(self, key):
        self.save()
        del self._items[key]

    def pop(self, key, default = undefined):
        self.save()
        if default is undefined:
            return self._items.pop(key)
        else:
            return self._items.pop(key, default)

    def popitem(self):
        self.save()
        return self._items.popitem()

    def setdefault(self, key, default = None):
        self.save()
        return self._items.setdefault(key, default)

    def update(self, other, **kwargs):
        self.save()
        self._items.update(other, **kwargs)

    # Expose beaker session api
    #------------------------------------------------------------------------------

    @property
    def id(self):
        return self._items.id

    def get_by_id(self, id):
        return self._items.get_by_id(id)

    @property
    def created(self):
        return self._items.created

    def delete(self):
        self._items.delete()

    def invalidate(self):
        self._items.invalidate()

    def load(self):
        self._items.load()

    def save(self):
        self._items.save()

    def persist(self):
        self._items.persist()

    def revert(self):
        self._items.revert()

    def lock(self):
        self._items.lock()

    def unlock(self):
        self._items.unlock()

    def dirty(self):
        return self._items.dirty()
    
    def accessed(self):
        return self._items.accessed(self)


session = Session()
