#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from unittest import TestCase

def get_user_schema():

    import re
    from cocktail.schema import Schema, Integer, String, Boolean

    return Schema(members = {
        "id": Integer(
            required = True,
            unique = True,
            min = 1
        ),
        "name": String(
            required = True,
            min = 4,
            max = 20,
            format = re.compile("^[a-zA-Z][a-zA-Z_0-9]*$")
        ),
        "enabled": Boolean(
            required = True,
            default = True
        )
    })


class User(object):
    id = None
    name = None
    enabled = True


class ImplicitCopyTestCase(TestCase):
    
    def test_implicit_schema_copy(self):
        
        from cocktail.schema import Schema, Adapter
        
        user_schema = get_user_schema()
        adapter = Adapter()
        
        self.assertTrue(adapter.implicit_copy)

        # Exporting schemas
        form_schema = Schema()
        adapter.export_schema(user_schema, form_schema)
        
        self.assertEqual(
            len(user_schema.members().keys()),
            len(form_schema.members().keys())
        )

        self.assertEqual(
            set(user_schema.members().keys()),
            set(form_schema.members().keys())
        )

        # Importing schemas
        user_schema_2 = Schema()
        adapter.import_schema(form_schema, user_schema_2)

        self.assertEqual(
            form_schema.members().keys(),
            user_schema_2.members().keys()
        )

    def test_implicit_object_copy(self):

        from cocktail.schema import Schema, Adapter

        user_schema = get_user_schema()
        adapter = Adapter()

        # Exporting objects
        user = User()
        user.id = 3
        user.name = "Kurt Russell"
        user.enabled = True

        form = {}
        adapter.export_object(user, form, user_schema)
                
        self.assertEqual(user.id, form["id"])
        self.assertEqual(user.name, form["name"])
        self.assertEqual(user.enabled, form["enabled"])

        # Importing objects
        user2 = User()
        adapter.import_object(form, user2, user_schema)

        self.assertEqual(user2.id, form["id"])
        self.assertEqual(user2.name, form["name"])
        self.assertEqual(user2.enabled, form["enabled"])

    def test_disabled_implicit_schema_copy(self):

        from cocktail.schema import Schema, Adapter
        
        user_schema = get_user_schema()
        form_schema = Schema()
        adapter = Adapter()
        adapter.implicit_copy = False

        adapter.export_schema(user_schema, form_schema)
        self.assertFalse(form_schema.members())

    def test_disabled_implicit_object_copy(self):

        from cocktail.schema import Schema, Adapter
                
        adapter = Adapter()
        adapter.implicit_copy = False

        user = User()
        user.id = 3
        user.name = "Kurt Russell"
        user.enabled = True

        form = {}
        
        adapter.export_object(user, form)
        self.assertFalse(form)

        adapter.import_object(user, form)
        self.assertFalse(form)


class CopyTestCase(TestCase):

    def test_simple_schema_copy(self):

        from cocktail.schema import Adapter, Schema, Copy

        adapter = Adapter()
        adapter.implicit_copy = False
        adapter.copy("id")
        adapter.copy("name")

        user_schema = get_user_schema()
        form_schema = Schema()
        
        adapter.export_schema(user_schema, form_schema)
        self.assertEqual(len(form_schema.members()), 2)
        self.assertEqual(
            set(form_schema.members().keys()),
            set(["id", "name"])
        )

    def test_simple_object_copy(self):

        from cocktail.schema import Adapter, Schema, Copy

        adapter = Adapter()
        adapter.implicit_copy = False
        adapter.copy("id")
        adapter.copy("name")
        
        user = User()
        user.id = 3
        user.name = "Kurt Russell"
        user.enabled = True

        form = {}
        adapter.export_object(user, form)
        self.assertEqual(form, {"id": user.id, "name": user.name})
    
    def test_object_copy_with_mapping(self):

        from cocktail.schema import Adapter, Schema, Copy

        adapter = Adapter()
        adapter.implicit_copy = False
        adapter.copy({"name": "user_name"})
        
        user = User()
        user.id = 3
        user.name = "Kurt Russell"
        user.enabled = True
        
        form = {}

        # Export
        adapter.export_object(user, form)
        self.assertEqual(form, {"user_name": user.name})

        # Import
        form["user_name"] = "Chuck Norris"
        adapter.import_object(form, user)
        self.assertEqual(user.id, 3)
        self.assertEqual(user.name, form["user_name"])
        self.assertEqual(user.enabled, True)


class ExclusionTestCase(TestCase):

    def test_exclude_undefined_member(self):

        from cocktail.schema import Adapter, Schema
        
        adapter = Adapter()
        adapter.exclude("fictitious_member")
        
        user_schema = get_user_schema()
        form_schema = Schema()
        adapter.export_schema(user_schema, form_schema)
        self.assertFalse("fictitious_member" in form_schema.members())

