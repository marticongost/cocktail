#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2008
"""
from time import time, mktime
from datetime import datetime, date, timedelta
from cocktail.modeling import DictWrapper
from cocktail.styled import styled

missing = object()


class ResourceLoader(DictWrapper):

    expiration = None
    resources = None
    enabled = True
    updatable = True
    verbose = False

    def __init__(self, load = None):
        resources = {}
        DictWrapper.__init__(self, resources)
        self.__resources = resources

        if load is not None:
            self.load = load

    def _drop_expired(self):

        if self.expiration:

            oldest_creation_time = time() - self.expiration

            for key, resource in self.__resources.items():
                if resource.creation < oldest_creation_time:
                    del self[key]

    def request(self, key, expiration = None, invalidation = None):
        try:
            return self.get_value(key, invalidation = invalidation)
        except KeyError:
            if self.verbose:
                print styled("ResourceLoader: Generating", "white", "red", "bold"),
                print key
            value = self.load(key)
            if self.enabled:
                self.set_value(key, value, expiration)
            return value

    def get_value(self, key, default = missing, invalidation = None):
        if self.enabled:
            resource = self.__resources.get(key, None)

            if resource is not None:

                if self.updatable \
                and not self._is_current(resource, invalidation, self.verbose):
                    if default is missing:
                        self._resource_expired(resource)
                        raise ResourceExpired(resource)
                else:
                    if self.verbose:
                        print styled("ResourceLoader: Recovering", "white", "green", "bold"),
                        print key
                    return resource.value

        if default is missing:
            raise KeyError("Undefined cache key: %s" % repr(key))

        return default

    def set_value(self, key, value, expiration = None):
        if self.verbose:
            print styled("ResourceLoader: Storing", "white", "pink", "bold"),
            print key,
            if expiration is None:
                print
            else:
                print styled("expiration:", "pink"), expiration
        self.__resources[key] = Resource(key, value, expiration)

    def load(self, key):
        pass

    def __delitem__(self, key):
        resource = self.__resources.get(key)
        if resource:
            self._resource_removed(resource)
        else:
            raise KeyError(key)

    def pop(self, key, default = missing):
        resource = self.__resources.get(key)
        if resource is None:
            if default is missing:
                raise KeyError(key)
            return default
        else:
            del self.__resources[key]
            self._resource_removed(resource)
            return resource

    def clear(self):
        resources = self.__resources.values()
        self.__resources.clear()
        for resource in resources:
            self._resource_removed(resource)

    def _is_current(self, resource, invalidation = None, verbose = False):

        # Expiration
        if resource.has_expired(default_expiration = self.expiration):
            if verbose:
                print styled(
                    "ResourceLoader: Resource expired",
                    "white", "brown", "bold"
                ), resource.key,
                if resource.expiration is None:
                    print self.expiration
                else:
                    print resource.expiration

            return False

        # Invalidation
        if callable(invalidation):
            invalidation = invalidation()

        if invalidation is not None:
            if isinstance(invalidation, datetime):
                invalidation = mktime(invalidation.timetuple())
            if invalidation > resource.creation:
                if verbose:
                    print styled(
                        "ResourceLoader: Resource invalidated",
                        "white", "brown", "bold"
                    ),
                    print resource.key, invalidation
                return False

        return True

    def _resource_removed(self, resource):
        pass

    def _resource_expired(self, resource):
        pass


class Resource(object):

    def __init__(self, key, value, expiration = None):
        self.key = key
        self.value = value
        self.creation = time()
        self.expiration = expiration

    def has_expired(self, default_expiration = None):

        expiration = self.expiration

        if expiration is None:
            expiration = default_expiration

        if expiration is None:
            return False

        elif isinstance(expiration, int):
            return time() - self.creation >= expiration

        elif isinstance(expiration, datetime):
            return datetime.now() >= expiration

        elif isinstance(expiration, date):
            return date.today() >= expiration

        elif isinstance(expiration, timedelta):
            return time() - self.creation >= expiration.total_seconds()


class ResourceExpired(KeyError):

    def __init__(self, resource):
        KeyError.__init__(self, "Resource expired: %s" % resource.key)
        self.resource = resource

