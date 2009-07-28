#-*- coding: utf-8 -*-
"""
Web services for persistent data types.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
import re
import simplejson
import cherrypy
from datetime import datetime, date, time
from cocktail.modeling import (
    cached_getter,
    ListWrapper,
    SetWrapper,
    DictWrapper
)
from cocktail.events import event_handler
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers.requesthandler import RequestHandler
from cocktail.controllers.usercollection import UserCollection
from cocktail.controllers.parameters import get_parameter

excluded_member = object()
_ids_expr = re.compile(r"\d+(,\d+)*")


class PersistentClassWebService(RequestHandler):
    """A controller that produces web service interfaces from a persistent data
    type definition.
    
    @ivar root_type: The root persistent data type exposed by the controller.
    @type root_type: L{PersistentObject<cocktail.persistence.PersistentObject>}
        subclass
    """
    root_type = None
    languages = None
    _subset_type = None

    @event_handler
    def handle_traversed(cls, event):
        cherrypy.response.headers["Content-Type"] = "text/plain"

    @event_handler
    def handle_exception_raised(cls, event):
        ex = event.exception
        cherrypy.response.body = event.source.dumps({
            "error": {
                "__class__": ex.__class__.__name__,
                "description": str(ex)
            }
        })
        event.handled = True

    def resolve(self, path):

        # Support direct access by id (spawn a new controller with a reduced
        # universe)
        if path and _ids_expr.match(path[0]):
            ids = path.pop(0).split(",")
            subset = filter(
                None,
                [self.type.get_instance(int(id)) for id in ids]
            )
            controller = self.__class__()
            
            # All items on the selected subset are of the same type: set it as
            # the active type for the request
            if len(set(item.__class__ for item in subset)) == 1:
                controller._subset_type = subset[0].__class__

            controller.query.base_collection = subset
            return controller
        else:
            return self

    @cached_getter
    def type(self):
        """The type specified by the current HTTP request.
        
        Will always be L{root_type} or one of its subclasses.
        @type: L{PersistentObject<cocktail.persistence.PersistentObject>}
            subclass
        """
        if self._subset_type:
            return self._subset_type

        cls = get_parameter(
            schema.Reference("class",
                class_family = self.root_type,
                default = self.root_type
            ),
            strict = True
        )

        if cls is None:
            raise ValueError("Wrong type selection")
 
        return cls

    class JSONEncoder(simplejson.JSONEncoder):

        def default(self, obj):
 
            if isinstance(obj, (ListWrapper, SetWrapper)):
                return list(obj)

            elif isinstance(obj, DictWrapper):
                return dict(obj.iteritems())

            elif isinstance(obj, (date, datetime)):
                return list(obj.timetuple())

            elif isinstance(obj, time):
                return (obj.hour, obj.minute, obj.second, obj.microsecond)

            elif isinstance(obj, schema.SchemaObject):
                
                values = {"__class__": obj.__class__.full_name}
                
                for key, member in obj.__class__.members().iteritems():                                        
                    
                    # TODO: allow selecting a subset of the available
                    # translations
                    if member.translated:
                        value = dict(
                            (
                                language,
                                self.get_member_value(obj, member, language)
                            )
                            for language in obj.translations
                        )
                    else:
                        value = self.get_member_value(obj, member)

                    if value is excluded_member:
                        continue
                    
                    values[key] = value

                return values

            return simplejson.JSONEncoder.default(self, obj)

        def get_member_value(self, obj, member, language = None):

            # TODO: implement joins
            if member.name == "translations":
                value = excluded_member
                
            elif isinstance(member, schema.Reference):
                value = obj.get(member)
                if value is not None:
                    if member.class_family:
                        value = value.full_name
                    else:
                        value = value.id

            elif isinstance(member, schema.Collection) \
            and member.related_type \
            and issubclass(member.related_type, schema.SchemaObject):
                value = obj.get(member)
                if value:
                    value = [item.id for item in value]
            else:
                value = obj.get(member, language)

            return value

    @cached_getter
    def json_encoder(self):
        return self.JSONEncoder(indent = 4)

    @cached_getter
    def query(self):
        """The selection of persistent instances affected by the current HTTP
        request.

        @type: L{Query<cocktail.persistence.Query>}
        """
        user_collection = UserCollection(self.type)
        self._init_user_collection(user_collection)
        user_collection.read()
        return user_collection.subset

    def _init_user_collection(self, user_collection):
        user_collection.allow_paging = False
        user_collection.allow_member_selection = False
        user_collection.selection_mode = 0

    def dumps(self, obj):
        return self.json_encoder.encode(obj)

    def __call__(self, **kwargs):
        return self.dumps(list(self.query))

    @cherrypy.expose
    def exists(self, **kwargs):
        return self.dumps(bool(self.query))

    @cherrypy.expose
    def count(self, **kwargs):
        return self.dumps(len(self.query))

    @cherrypy.expose
    def new(self, **kwargs):
 
        # Make sure the operation can only be performed using a POST request
        if cherrypy.request.method != "POST":
            raise cherrypy.HTTPError(400, "Wrong HTTP method")

        instance = self._create_instance()
        self._init_new_instance(instance)
        self._store_new_instance(instance)
        datastore.commit()

        # Return the created instance
        return self.dumps({"item": instance})

    def _create_instance(self):
        return self.type()
    
    def _init_new_instance(self, instance):

        # Initialize the instance with data from the request
        get_parameter(
            instance.__class__,
            target = instance,
            prefix = "item.",
            languages = self.languages,
            skip_undefined = True,
            implicit_booleans = False,
            enable_defaults = False,
            strict = False
        )

        # Validate the new instance
        for error in instance.__class__.get_errors(instance):
            raise error
        
    def _store_new_instance(self, instance):
        instance.insert()

    @cherrypy.expose
    def update(self, **kwargs):

        # Make sure the operation can only be performed using a POST request
        if cherrypy.request.method != "POST":
            raise cherrypy.HTTPError(400, "Wrong HTTP method")
        
        update_count = 0

        for instance in self.query:
            self._update_instance(instance)
            update_count += 1

        datastore.commit()
        
        # Return the number of affected instances
        return self.dumps({"updated_items": update_count})

    def _update_instance(self, instance):

        # Use a temporary object to validate incomming data. This is necessary
        # to avoid overriding indexed values, which would deny some validations
        # (ie. unique value checks).
        adapter = schema.Adapter()
        data = {}
        adapter.export_object(instance, data, instance.__class__)

        # Load and validate the data from the request
        get_parameter(
            instance.__class__,
            target = data,
            prefix = "item.",
            languages = self.languages,
            skip_undefined = True,
            implicit_booleans = False,
            enable_defaults = False,
            strict = False
        )

        for error in instance.__class__.get_errors(
            data,
            persistent_object = instance
        ):
            raise error

        # Transfer the validated data into the updated instance
        adapter.import_object(data, instance, instance.__class__)

    @cherrypy.expose
    def delete(self, **kwargs):

        # Make sure the operation can only be performed using a POST request
        if cherrypy.request.method not in ("POST", "DELETE"):
            raise cherrypy.HTTPError(400, "Wrong HTTP method")

        query = self.query
        count = len(query)
        self._delete_instances(query)
        datastore.commit()
        
        # Return the number of deleted instances
        return self.dumps({"deleted_items": count})

    def _delete_instances(self, query):
        query.delete_items()

