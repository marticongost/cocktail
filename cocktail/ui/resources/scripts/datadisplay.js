/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2017
-----------------------------------------------------------------------------*/

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
                    if (newValue) {

                        // Set the display's value when a new data context is assigned
                        this.value = newValue.value;

                        // Reflect the context in the display's attributes
                        if (newValue.member.name) {
                            this.setAttribute("member", newValue.member.name);
                        }
                        else {
                            this.removeAttribute("member");
                        }

                        if (newValue.language) {
                            this.setAttribute("language", newValue.language);
                        }
                        else {
                            this.removeAttribute("language");
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
                type: (obj) => obj.dataBinding.member,
                reflected: true
            },
            formLabelDisposition: {
                type: "string",
                reflected: true
            }
        }
    }
}

{
    const MEMBER = Symbol();
    const OBJECT = Symbol();
    const LANGUAGE = Symbol();
    const PARENT = Symbol();
    const VALUE = Symbol();

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
            this[VALUE] = (value === undefined) ? this.getValue() : value;
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
            let value = object[this[MEMBER].name];
            if (this[MEMBER].translated) {
                language = language || this[LANGUAGE];
                if (language) {
                    value = value[language];
                }
            }
            return value;
        }

        child(object, member, language = null) {
            let child = new this.constructor(object, member, language);
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

        extend() {
            let child = new this.constructor();
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

// A display factory for read only values
cocktail.ui.displays = new cocktail.ui.DisplayFactory("cocktail.ui.display");
cocktail.schema.Member.prototype[cocktail.ui.display] =
    (dataBinding, parameters) => parameters.wrapRawValues ? cocktail.ui.Value : null;

// A display factory for editable values
cocktail.ui.formControls = new cocktail.ui.DisplayFactory("cocktail.ui.formControl");

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

