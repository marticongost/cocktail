#-*- coding: utf-8 -*-
"""
Provides a mix-in class for controllers that read schema based objects.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2009
"""
import cherrypy
from cocktail.modeling import getter, cached_getter
from cocktail import schema
from cocktail.persistence import PersistentClass
from cocktail.controllers.controller import Controller
from cocktail.controllers.parameters import get_parameter


class FormControllerMixin(object):
    """Mix-in class for controllers that read schema based objects.
    
    @var form_model: The class of the edited object.
    @type form_model: L{SchemaObject subclass
                        <cocktail.schema.schemaobject.SchemaObject>}
    """    
    form_model = None
    _form_instance = None
    _form_instance_is_new = True

    def __init__(self):
        self.processed.append(self._handle_processed)

    @cached_getter
    def form_schema(self):
        """The schema that describes the form.
        @type: L{Schema<cocktail.schema.schema.Schema>}
        """
        form_model = self.form_model
        
        if form_model is None:
            raise ValueError("Form model missing")
        
        form_adapter = self.form_adapter

        if not form_adapter.has_rules():
            return form_model

        form_schema = schema.Schema(form_model.name + "Form")
        form_adapter.export_schema(form_model, form_schema)
        return form_schema

    @cached_getter
    def form_data(self):
        """A dictionary that contains the user's input.
        @type: dict
        """
        form_data = {}

        # First load: set the initial state for the form
        if not self.submitted:
            self._init_form_data(form_data)
        
        # Form submitted: read request data
        else:
            self._read_form_data(form_data)

        return form_data
    
    def _init_form_data(self, form_data):
        """Set the form state on first load.
        
        @param form_data: The dictionary representing the form state.
        @type form_data: dict
        """
        if self.form_instance_is_new:
            self._apply_form_defaults(form_data)
        else:
            self._apply_instance_data(form_data)

    def _apply_form_defaults(self, form_data):
        """Initialize the form state with defaults supplied by the form's
        schema.
        
        @param form_data: The dictionary representing the form state.
        @type form_data: dict
        """
        self.form_schema.init_instance(form_data)
        get_parameter(
            self.form_schema,
            target = form_data,
            skip_undefined = True
        )

    def _apply_instance_data(self, form_data):
        """Initialize the form state with data from the edited instance.

        @param form_data: The dictionary representing the form state.
        @type form_data: dict
        """
        self.form_adapter.export_object(
            self.form_instance,
            form_data,
            source_schema = self.form_model,
            target_schema = self.form_schema
        )

    def _read_form_data(self, form_data):
        """Read data from the request.
        
        @param form_data: The dictionary that request data is read into.
        @type form_data: dict
        """
        get_parameter(
            self.form_schema,
            target = form_data,
            **self.form_reader_params
        )

    @cached_getter
    def form_reader_params(self):
        """The set of parameters to pass to
        L{get_parameter<cocktail.controllers.parameters.get_parameter>} when
        reading data from the form.
        @type: dict
        """
        return {"strict": False, "enable_defaults": False}

    @cached_getter
    def form_adapter(self):
        """The adapter used to pass data to and from the model and the form.
        @type: L{Adapter<cocktail.schema.schemaadapter.Adapter>}
        """
        adapter = schema.Adapter()
        return adapter
        
    def _get_form_instance(self):
        if self._form_instance is None:
            if self.form_model:
                self._form_instance = self._create_form_instance()
                
        return self._form_instance

    def _set_form_instance(self, form_instance):
        self._form_instance = form_instance
        self._form_instance_is_new = (form_instance is None)

    form_instance = property(
        _get_form_instance,
        _set_form_instance,
        doc = """The instance produced by the form.
        @type: L{SchemaObject<cocktail.schema.schemaobject.SchemaObject>}
            or dict
        """
    )

    def _create_form_instance(self):
        if isinstance(self.form_model, type):
            return self.form_model()
        else:
            return {}

    def _apply_form_data(self):
        """Fill the edited instance with data from the form."""
        self.form_adapter.import_object(
            self.form_data,
            self.form_instance,
            source_schema = self.form_schema,
            target_schema = self.form_model
        )

    @getter
    def form_instance_is_new(self):
        """Indicates if the form is being used to create a new instance of the
        model (True) or to edit an existing object (False).
        @type: bool
        """
        return self._form_instance_is_new

    @cached_getter
    def form_errors(self):
        """A list containing validation errors for the current form state.
        @type: L{ErrorList<cocktail.schema.errorlist.ErrorList>}
        """
        return schema.ErrorList(
            self.form_schema.get_errors(
                self.form_data,
                **self.form_validation_context
            )
            if self.submitted
            else ()
        )

    @cached_getter
    def form_validation_context(self):
        context = {}

        if isinstance(self.form_model, PersistentClass):
            context["persistent_object"] = self.form_instance

        return context

    @cached_getter
    def submitted(self):
        return cherrypy.request.method == "POST"

    @cached_getter
    def valid(self):
        return not self.form_errors

    def submit(self):
        self._apply_form_data()

    def _handle_processed(self, event):
        
        # Extend the output with form data
        self.output.update(
            form_data = self.form_data,
            form_schema = self.form_schema,
            form_errors = self.form_errors
        )

