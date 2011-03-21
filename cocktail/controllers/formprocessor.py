#-*- coding: utf-8 -*-
u"""Provides the `FormProcessor` and `Form` classes.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.modeling import getter, cached_getter, camel_to_underscore
from cocktail import schema
from cocktail.persistence import PersistentClass, transactional
from cocktail.controllers.parameters import get_parameter
from cocktail.controllers.requestproperty import clear_request_properties


class FormProcessor(object):
    """A mixin controller class that automates the processing of one or more
    forms.
    """
    is_transactional = False

    def __init__(self):        
        self.processed.append(self.__handle_processed)

    @cached_getter
    def forms(self):
        """The list of `forms <Form>` defined by the controller."""
        forms = {}        
        
        for key in dir(self.__class__):
            member = getattr(self.__class__, key, None)
            if isinstance(member, type) and issubclass(member, Form):
                form = member(self)
                forms[form.form_id] = form

        return forms

    @cached_getter
    def action(self):
        """The action selected by the user.
        
        The chosen action is paired with the `~Form.actions>` attribute of each
        form defined by the controller to determine which forms should be
        submitted.
        """
        return get_parameter("action")

    @cached_getter
    def submitted(self):
        return cherrypy.request.method == "POST"

    @cached_getter
    def valid(self):
        return all(form.valid for form in self.submitted_forms)

    @cached_getter
    def submitted_forms(self):
        """A list of all the `forms` in the controller that have been submitted
        in the current request.
        """
        if not self.submitted:
            return []
        else:
            forms = []
            form_ids = set()

            def find_submitted_forms(form):
                if form.form_id not in form_ids and form.submitted:
                    form_ids.add(form.form_id)

                    if form.process_after:
                        for dependency_id in form.process_after:
                            dependency = self.forms.get(dependency_id)
                            if dependency:
                                find_submitted_forms(dependency)
                
                    forms.append(form)
                            
            for form in self.forms.itervalues():
                find_submitted_forms(form)

            return forms

    def submit(self):

        if self.is_transactional:
            self._run_transaction()
        else:
            self.submit_forms()

        for form in self.submitted_forms:
            form.after_submit()

    @transactional(before_retrying = clear_request_properties)
    def _run_transaction(self):
        self.transaction()

    def transaction(self):
        self.submit_forms()    

    def submit_forms(self):
        for form in self.submitted_forms:
            form.submit()

    @cached_getter
    def errors(self):
        errors = schema.ErrorList()

        for form in self.submitted_forms:
            for error in form.errors:
                errors.add(error)

        return errors

    def __handle_processed(self, event):
        self.output["forms"] = self.forms
        self.output["form_errors"] = self.errors


class Form(object):
    """A description of a form based on a schema."""
    controller = None
    actions = (None,)
    process_after = ()

    def __init__(self, controller):
        self.controller = controller

    def __str__(self):
        return "%s in %s" % (self.form_id, self.controller)

    @cached_getter
    def model(self):

        source_instance = self.source_instance

        if source_instance is not None \
        and isinstance(source_instance, schema.SchemaObject):
            return source_instance.__class__

        return schema.Schema(self.__class__.__name__)

    @cached_getter
    def form_id(self):
        """The name given to the form by its `controller`."""
        return camel_to_underscore(self.__class__.__name__)
    
    @cached_getter
    def submitted(self):
        """Indicates if this particular form has been submitted in the current
        request.
        """
        return self.controller.submitted \
           and self.controller.action in self.actions

    def submit(self):
        """Load and handle form data when the form is submitted."""
        self.apply_form_data()

    def after_submit(self):
        """Perform additional actions after all forms have been submitted."""
        pass

    @cached_getter
    def valid(self):
        """Indicates if the form is valid and can be submitted."""
        return not self.errors

    @cached_getter
    def errors(self):
        """The `list of validation errors<cocktail.schema.errorlist.ErrorList>`
        for the current form state.
        """
        return schema.ErrorList(
            self.schema.get_errors(
                self.data,
                **self.validation_context
            )
            if self.submitted
            else ()
        )

    @cached_getter
    def adapter(self):
        """The adapter used to obtain the form's customized `schema` from the
        form's `model`.
        """
        return schema.Adapter()

    @cached_getter
    def schema(self):
        """A schema describing the fields and validation logic that make up the
        form.
        """
        if self.model is None:
            raise ValueError("No form model specified for %s" % self)
        
        adapted_schema = schema.Schema(self.form_id)
        return self.adapter.export_schema(self.model, adapted_schema)
    
    @cached_getter
    def data(self):
        """A dictionary containing the user's input."""

        data = {}

        # First load: set the initial state for the form
        if not self.submitted:
            self.init_data(data)
        
        # Form submitted: read request data
        else:
            self.read_data(data)

        return data

    def init_data(self, data):
        """Set the form state on first load.
        
        :param data: The dictionary representing the form state.
        :type data: dict
        """
        if self.source_instance is None:
            # First, apply defaults specified by the form schema
            self.apply_defaults(data)
            
            # Then, selectively override these with any pre-supplied parameter
            # (useful to pass parameters to a form page)
            get_parameter(
                self.schema,
                target = data,
                undefined = "skip",
                errors = "ignore"
            )
        else:
            self.apply_instance_data(data)
    
    def apply_defaults(self, data):
        """Initialize the form state with defaults supplied by the form's
        schema.
        
        :param data: The dictionary representing the form state.
        :type data: dict
        """
        self.schema.init_instance(data)    

    def apply_instance_data(self, data):
        """Initialize the form state with data from the edited instance.

        :param data: The dictionary representing the form state. The method
            should update it with data from the source instance.
        :type data: dict
        """
        self.adapter.export_object(
            self.instance,
            data,
            source_schema = self.model,
            target_schema = self.schema
        )

    def read_data(self, data):
        """Update the form state with data read from the request.
        
        :param data: The dictionary that request data is read into.
        :type data: dict
        """
        get_parameter(
            self.schema,
            target = data,
            **self.reader_params
        )

    @cached_getter
    def reader_params(self):
        """The set of parameters to pass to
        `get_parameter <cocktail.controllers.parameters.get_parameter>` when
        reading data from the form.        
        """
        return {"errors": "ignore", "undefined": "set_none"}

    @cached_getter
    def instance(self):
        """The instance produced by the form. 
        
        Depending on the form's model, it will be a dictionary or a 
        `SchemaObject <cocktail.schema.schemaobject.SchemaObject>` instance.
        """
        return self.source_instance or self.create_instance()

    @cached_getter
    def source_instance(self):
        """An existing instance that should be edited by the form."""
        return None

    def create_instance(self):
        if isinstance(self.model, type):
            return self.model()
        else:
            return {}

    def apply_form_data(self):
        """Fill the edited instance with data from the form."""
        self.adapter.import_object(
            self.data,
            self.instance,
            source_schema = self.schema,
            target_schema = self.model
        )

    @cached_getter
    def validation_context(self):
        """Context supplied to the form validation process."""
        context = {}

        if isinstance(self.model, PersistentClass):
            context["persistent_object"] = self.instance

        return context

