/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2017
-----------------------------------------------------------------------------*/

// Display factories
{
    const PARENT = Symbol();
    cocktail.ui.chooseDisplay = Symbol.for("cocktail.ui.chooseDisplay");
    cocktail.ui.chooseDefaultDisplay = Symbol.for("cocktail.ui.chooseDefaultDisplay");

    cocktail.schema.Member.prototype[cocktail.ui.chooseDisplay] = function (factory, dataBinding, parameters = null) {
        return this[factory.symbol];
    }

    cocktail.schema.Member.prototype[cocktail.ui.chooseDefaultDisplay] = function (factory, dataBinding, parameters = null) {
        return this.constructor[factory.symbol];
    }

    cocktail.schema.Reference.prototype[cocktail.ui.chooseDefaultDisplay] = function (factory, dataBinding, parameters = null) {
        let type = this.type;
        while (type) {
            let component = type[factory.symbol];
            if (component) {
                return component;
            }
            type = type.base;
        }
        return cocktail.schema.Member.prototype[cocktail.ui.chooseDefaultDisplay].call(this, factory, dataBinding, parameters);
    }

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
            let component = this.resolveComponent(
                dataBinding.member[cocktail.ui.chooseDisplay](this, dataBinding, parameters),
                dataBinding,
                parameters
            );

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

            let component = this.resolveComponent(
                dataBinding.member[cocktail.ui.chooseDefaultDisplay](this, dataBinding, parameters),
                dataBinding,
                parameters
            );

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
            if (!parameters) {
                parameters = {};
            }
            parameters.displayFactory = this;
            if (parameters.wrapRawValues === undefined) {
                parameters.wrapRawValues = true;
            }
            while (component && !component.create) {
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
cocktail.schema.Member[cocktail.ui.display] =
    (dataBinding, parameters) => parameters.wrapRawValues ? cocktail.ui.Value : null;
cocktail.schema.Collection.prototype[cocktail.ui.display] = () => cocktail.ui.List;

// A display factory for read only values, without interaction (ie. to include on Selectable lists)
cocktail.ui.inertDisplays = cocktail.ui.displays.extend("cocktail.ui.inertDisplay");

// A display factory for editable values
cocktail.ui.formControls = new cocktail.ui.FormControlsDisplayFactory("cocktail.ui.formControl");

// A display factory for read only form controls
cocktail.ui.readOnlyFormControls = cocktail.ui.displays.extend("cocktail.ui.readOnlyFormControl");

// A display factory for the entries of collection editors
cocktail.ui.collectionEditorControls = cocktail.ui.formControls.extend("cocktail.ui.collectionEditorControl");

// A display factory for the entries of autocomplete forms
cocktail.ui.autocompleteDisplays = cocktail.ui.inertDisplays.extend("cocktail.ui.autocompleteDisplay");

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

// A symbol that makes it possible to specify the component used by the different groups
// of a schema
cocktail.ui.formGroupComponents = Symbol("cocktail.ui.formGroupComponents");

// A symbol indicating the set of fields that should be included in data source requests
// to display a member. Defaults to a single field, with the member's name. Set to null
// to exclude the member from data source requests.
{
    cocktail.ui.dataSourceFields = Symbol("cocktail.ui.dataSourceFields");

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

// A symbol that allows members to set the width for their column on Table
// instances
cocktail.ui.columnWidth = Symbol.for("cocktail.ui.columnWidth");

