#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
import pickle
from cStringIO import StringIO
from cocktail.pkgutils import get_full_name
from cocktail.schema import Schema, Member
from cocktail.persistence.persistentobject import PersistentObject

def dumps(obj):
    src = StringIO()
    p = pickle.Pickler(src)
    p.persistent_id = _persistent_id
    p.dump(obj)
    return src.getvalue()

def loads(datastream):
    dst = StringIO(datastream)
    up = pickle.Unpickler(dst)
    up.persistent_load = _persistent_load
    return up.load()

def _get_schema(name):
    for schema in PersistentObject.derived_schemas():
        if name == get_full_name(schema):
            return schema

def _persistent_id(obj):
    if isinstance(obj, PersistentObject):
        return "instance: %s %s" % (get_full_name(type(obj)), str(obj.id))

    if isinstance(obj, Member) and obj.schema:
        return "member: %s.%s" % (get_full_name(obj.schema), obj.name)

    return None

def _persistent_load(persid):

    pers_keys = persid.split()
    obj_type = pers_keys[0]

    if obj_type == "instance:":
        schema = _get_schema(pers_keys[1])
        id = int(pers_keys[2])
        return schema.get_instance(id)
    elif obj_type == "member:":
        components = pers_keys[1].split(".")
        name = '.'.join(components[:-1])
        member_name = components[-1]
        obj = _get_schema(name)
        return getattr(obj, member_name, None)
    else:
        raise pickle.UnpicklingError, 'Invalid persistent id'

