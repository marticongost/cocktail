/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2017
-----------------------------------------------------------------------------*/

{
    const CHANGES = Symbol.for("cocktail.ui.dataDisplay.CHANGES");

    let getModelChanges = function (model) {
        return model[CHANGES] || (model[CHANGES] = new cocktail.ui.Observable());
    }

    let triggerInvalidation = function (model, change) {
        change.model = model;
        getModelChanges(model).trigger(change);
    }

    let subscribe = function (display, dataBinding) {
        if (display.parentNode && dataBinding && dataBinding.member.relatedType) {
            let model = dataBinding.member.relatedType.originalMember;
            let changes = getModelChanges(model);
            display.observe(changes);
        }
    }

    let unsubscribe = (display, dataBinding) => {
        if (dataBinding && dataBinding.member.relatedType) {
            let model = dataBinding.member.relatedType.originalMember;
            let changes = getModelChanges(model);
            display.stopObserving(changes);
        }
    }

    cocktail.ui.objectCreated = function (model, record) {
        triggerInvalidation(model, {type: "create", record});
    }

    cocktail.ui.objectModified = function (model, id, oldState, newState) {
        triggerInvalidation(model, {
            type: "modify",
            id,
            oldState,
            newState
        });
    }

    cocktail.ui.objectDeleted = function (model, id) {
        triggerInvalidation(model, {type: "delete", id});
    }

    cocktail.ui.modelInstancesDeleted = function (model) {
        triggerInvalidation(model, {type: "delete"});
    }

    cocktail.ui.addAnnotations = Symbol.for("cocktail.ui.addAnnotations");
    cocktail.ui.removeAnnotations = Symbol.for("cocktail.ui.removeAnnotations");

    {
        const CACHE = new WeakMap();

        cocktail.ui.getMemberTypes = function (memberType) {
            let memberTypeStr = CACHE.get(memberType);
            if (!memberTypeStr) {
                let memberTypeList = [];
                while (memberType !== cocktail.schema.Member) {
                    memberTypeList.push(memberType.name);
                    memberType = Object.getPrototypeOf(memberType);
                }
                memberTypeStr = memberTypeList.join(" ");
                CACHE.set(memberType, memberTypeStr);
            }
            return memberTypeStr;
        }
    }

    cocktail.schema.Member.prototype[cocktail.ui.addAnnotations] = function (element) {
        element.setAttribute("member", this.name);
        element.setAttribute("memberType", cocktail.ui.getMemberTypes(this.constructor));
    }

    cocktail.schema.Member.prototype[cocktail.ui.removeAnnotations] = function (element) {
        element.removeAttribute("member");
        element.removeAttribute("memberType");
    }

    cocktail.schema.Collection.prototype[cocktail.ui.addAnnotations] = function (element) {
        cocktail.schema.Member.prototype[cocktail.ui.addAnnotations].call(this, element);
        if (this.items) {
            element.setAttribute("itemsType", cocktail.ui.getMemberTypes(this.items.constructor));
        }
    }

    cocktail.schema.Collection.prototype[cocktail.ui.removeAnnotations] = function (element) {
        cocktail.schema.Member.prototype[cocktail.ui.removeAnnotations].call(this, element);
        element.removeAttribute("itemsType");
    }

    cocktail.ui.dataDisplay = (cls) => class DataDisplay extends cls {

        static get componentProperties() {
            return {
                dataBinding: {

                    // Accept arbitrary objects.
                    // This allows to set the property using an object literal, instead of
                    // having to instantiate cocktail.ui.DataBinding explicitly.
                    normalization: function (value) {
                        if (value && !(value instanceof cocktail.ui.DataBinding)) {
                            value = new cocktail.ui.DataBinding(
                                value.object,
                                value.member,
                                value.language,
                                value.value
                            );
                        }
                        return value;
                    },
                    changedCallback: function (oldValue, newValue) {

                        unsubscribe(this, oldValue);
                        subscribe(this, newValue);

                        if (newValue) {

                            // Set the display's value when a new data context is assigned
                            this.value = newValue.value;

                            // Reflect the context in the display's attributes
                            if (newValue.member.name) {
                                newValue.member[cocktail.ui.addAnnotations](this);
                            }
                            else {
                                newValue.member[cocktail.ui.removeAnnotations](this);
                            }

                            if (newValue.language) {
                                this.setAttribute("language", newValue.language);
                                this.setAttribute("dir", cocktail.ui.directionality[newValue.language]);
                            }
                            else {
                                this.removeAttribute("language");
                                this.removeAttribute("dir");
                            }
                        }
                        else {
                            this.removeAttribute("member");
                            this.removeAttribute("language");
                        }
                    }
                },
                displayFactory: {},
                value: {
                    type: (obj) => obj.dataBinding && obj.dataBinding.member || cocktail.ui.Property.types.string,
                    reflected: true
                },
                formLabelDisposition: {
                    type: "string",
                    reflected: true
                }
            }
        }

        connectedCallback() {
            super.connectedCallback();
            subscribe(this, this.dataBinding);
        }

        disconnectedCallback() {
            super.disconnectedCallback();
            unsubscribe(this, this.dataBinding);
        }

        invalidation(change) {
            if (
                this.value
                && change.type == "modify"
                && this.getAttribute("value") === change.id
            ) {
                this.value = change.newState;
            }
        }

        linkDisplay(linkedDisplay) {
            this.addEventListener("dataBindingChanged", (e) => {
                linkedDisplay.dataBinding = e.detail.newValue;
            });
            cocktail.ui.link(
                this,
                linkedDisplay,
                "value",
                (display, linkedDisplay) => {
                    if (display.dataBinding === linkedDisplay.dataBinding) {
                        linkedDisplay.value = display.value;
                    }
                },
                (linkedDisplay, display) => {
                    if (display.dataBinding === linkedDisplay.dataBinding) {
                        display.value = linkedDisplay.value;
                    }
                }
            );
        }

        getJSONValue() {
            if (!this.dataBinding) {
                return {};
            }
            return this.dataBinding.member.toJSONValue(this.value);
        }
    }
}

{
    const MEMBER = Symbol("cocktail.ui.DataBinding.MEMBER");
    const OBJECT = Symbol("cocktail.ui.DataBinding.OBJECT");
    const LANGUAGE = Symbol("cocktail.ui.DataBinding.LANGUAGE");
    const PARENT = Symbol("cocktail.ui.DataBinding.PARENT");
    const VALUE = Symbol("cocktail.ui.DataBinding.VALUE");

    cocktail.ui.DataBinding = class DataBinding {

        constructor(object, member, language = null, value = undefined) {

            if (!member) {
                throw new cocktail.ui.InvalidDataBindingError(
                    "Can't create a data binding without specifying a member"
                );
            }

            this[OBJECT] = object;
            this[MEMBER] = member;
            this[LANGUAGE] = language;
            this[VALUE] = (value === undefined) ? this.getValue(language) : value;
        }

        get object() {
            return this[OBJECT];
        }

        get member() {
            return this[MEMBER];
        }

        get language() {
            return this[LANGUAGE];
        }

        get parent() {
            return this[PARENT];
        }

        get value() {
            return this[VALUE];
        }

        getValue(language = null) {
            let object = this[OBJECT];
            if (object === undefined) {
                return undefined;
            }
            return this[MEMBER].getObjectValue(object, language);
        }

        child(object, member, language = null, value = undefined) {
            let child = new this.constructor(object, member, language, value);
            child[PARENT] = this;
            return child;
        }
    }
}

cocktail.ui.InvalidDataBindingError = class InvalidDataBindingError {

    constructor(message) {
        this.message = message;
    }

    toString() {
        return this.message;
    }
}

{
    const PARENT = Symbol();

    cocktail.ui.DisplayFactory = class DisplayFactory {

        constructor(symbolName) {
            this.symbol = Symbol(symbolName);
            cocktail.setVariable(symbolName, this.symbol);
        }

        get parent() {
            return this[PARENT];
        }

        extend(symbolName, cls = null) {
            let child = new (cls || this.constructor)(symbolName);
            child[PARENT] = this;
            return child;
        }

        createDisplay(dataBinding, parameters = null) {
            let component = this.getComponent(dataBinding, parameters);
            let display;
            if (component) {
                display = component.create();
                display.displayFactory = this;
                display.dataBinding = dataBinding;
            }
            return display;
        }

        requireDisplay(dataBinding, parameters = null) {
            let display = this.createDisplay(dataBinding, parameters);
            if (!display) {
                throw new cocktail.ui.DisplayRequiredError(this, dataBinding, parameters);
            }
            return display;
        }

        getComponent(dataBinding, parameters = null) {
            return (
                   this.getCustomComponent(dataBinding, parameters)
                || this.getDefaultComponent(dataBinding, parameters)
            );
        }

        getCustomComponent(dataBinding, parameters = null) {

            let member = dataBinding.member;
            let component = this.resolveComponent(member[this.symbol], dataBinding, parameters);

            if (!component) {
                if (this[PARENT]) {
                    component = this[PARENT].getCustomComponent(dataBinding, parameters);
                }
                else {
                    component = null;
                }
            }

            return component;
        }

        getDefaultComponent(dataBinding, parameters = null) {

            let memberType = dataBinding.member.constructor;
            let component = this.resolveComponent(memberType[this.symbol], dataBinding, parameters);

            if (!component) {
                if (this[PARENT]) {
                    component = this[PARENT].getDefaultComponent(dataBinding);
                }
                else {
                    component = null;
                }
            }

            return component;
        }

        resolveComponent(component, dataBinding, parameters) {
            if (component && !cocktail.ui.isComponent(component)) {
                if (!parameters) {
                    parameters = {};
                }
                if (parameters.wrapRawValues === undefined) {
                    parameters.wrapRawValues = true;
                }
                component = component(dataBinding, parameters);
            }
            return component;
        }
    }
}

cocktail.ui.FormControlsDisplayFactory = class FormControlsDisplayFactory extends cocktail.ui.DisplayFactory {

    getDefaultComponent(dataBinding, parameters = null) {
        let control;
        if (dataBinding.member.enumeration) {
            control = this.getEnumerationControl(dataBinding, parameters);
        }
        return control || super.getDefaultComponent(dataBinding, parameters);
    }

    getEnumerationControl(dataBinding, parameters = null) {
        return this.enumerationControl
            && this.resolveComponent(this.enumerationControl, dataBinding, parameters);
    }
}

cocktail.ui.DisplayRequiredError = class DisplayRequiredError {

    constructor(displayFactory, dataBinding, parameters) {
        this.displayFactory;
        this.dataBinding = dataBinding;
        this.parameters = parameters;
    }

    toString() {
        return `${this.displayFactory} couldn't create a display for ${this.dataBinding.member}`;
    }
}

// A display factory for read only values
cocktail.ui.displays = new cocktail.ui.DisplayFactory("cocktail.ui.display");
cocktail.schema.Member.prototype[cocktail.ui.display] =
    (dataBinding, parameters) => parameters.wrapRawValues ? cocktail.ui.Value : null;

cocktail.schema.Reference.prototype[cocktail.ui.display] = () => cocktail.ui.Value;

// A display factory for editable values
cocktail.ui.formControls = new cocktail.ui.FormControlsDisplayFactory("cocktail.ui.formControl");

// A display factory for read only form controls
cocktail.ui.readOnlyFormControls = cocktail.ui.displays.extend("cocktail.ui.readOnlyFormControl");

// A display factory for the entries of collection editors
cocktail.ui.collectionEditorControls = cocktail.ui.formControls.extend("cocktail.ui.collectionEditorControl");

// A display factory for the entries of autocomplete forms
cocktail.ui.autocompleteDisplays = cocktail.ui.displays.extend("cocktail.ui.autocompleteDisplay");

// A symbol that allows members to specify their preferred disposition for their label
// in a form
cocktail.ui.formLabelDisposition = Symbol("cocktail.ui.formLabelDisposition");

// A symbol that controls wether a member should be included in the default selection
// of visible members on controls that allow toggling member visibility (such as
// cocktail.ui.Table)
cocktail.ui.listedByDefault = Symbol("cocktail.ui.listedByDefault");
cocktail.schema.Member.prototype[cocktail.ui.listedByDefault] = true;

// A symbol that controls wether a member should be included in a form, or if it
// should be presented as a read only field
cocktail.ui.editable = Symbol("cocktail.ui.editable");
cocktail.ui.EDITABLE = Symbol("cocktail.ui.EDITABLE");
cocktail.ui.NOT_EDITABLE = Symbol("cocktail.ui.NOT_EDITABLE");
cocktail.ui.READ_ONLY = Symbol("cocktail.ui.READ_ONLY");
cocktail.schema.Member.prototype[cocktail.ui.editable] = cocktail.ui.EDITABLE;

// A symbol that allows to distribute the members of a data display into different groups
// (f. eg. form fieldsets)
cocktail.ui.group = Symbol("cocktail.ui.group");

// A symbol indicating the set of fields that should be included in data source requests
// to display a member. Defaults to a single field, with the member's name. Set to null
// to exclude the member from data source requests.
cocktail.ui.dataSourceFields = Symbol("cocktail.ui.dataSourceFields");

{
    const VALUE = Symbol();
    Object.defineProperty(
        cocktail.schema.Member.prototype,
        cocktail.ui.dataSourceFields,
        {
            get() {
                let fields = this[VALUE];
                return (fields === undefined) ? [this.name] : fields;
            },
            set (value) {
                this[VALUE] = value;
            }
        }
    );
}
