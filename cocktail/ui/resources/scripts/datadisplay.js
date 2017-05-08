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
            uiGenerator: {},
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

    cocktail.ui.UIGenerator = class UIGenerator {

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

        createDisplay(dataBinding) {
            let component = this.getComponent(dataBinding);
            let display;
            if (component) {
                display = component.create();
                display.uiGenerator = this;
                display.dataBinding = dataBinding;
            }
            return display;
        }

        getComponent(dataBinding) {
            return this.getCustomComponent(dataBinding) || this.getDefaultComponent(dataBinding);
        }

        getCustomComponent(dataBinding) {

            let member = dataBinding.member;
            let component = member[this.symbol];

            if (component && !cocktail.ui.isComponent(component)) {
                component = component(dataBinding);
            }

            if (!component) {
                if (this[PARENT]) {
                    component = this[PARENT].getCustomComponent(dataBinding);
                }
                else {
                    component = null;
                }
            }

            return component;
        }

        getDefaultComponent(dataBinding) {

            let memberType = dataBinding.member.constructor;
            let component = memberType[this.symbol];

            if (component && !cocktail.ui.isComponent(component)) {
                component = component(dataBinding);
            }

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
    }
}

cocktail.ui.displays = new cocktail.ui.UIGenerator("cocktail.ui.display");
cocktail.ui.formControls = new cocktail.ui.UIGenerator("cocktail.ui.formControl");
cocktail.ui.formLabelDisposition = Symbol("cocktail.ui.formLabelDisposition");

// A symbol that controls wether a member should be included in the default selection
// of visible members on controls that allow toggling member visibility (such as
// cocktail.ui.Table)
cocktail.ui.listedByDefault = Symbol("cocktail.ui.listedByDefault");
cocktail.schema.Member.prototype[cocktail.ui.listedByDefault] = true;

cocktail.ui.COPY_VALUE = Symbol("cocktail.ui.COPY_VALUE");

cocktail.ui.copyValue = function (value) {

    if (
        value === null
        || value === undefined
        || value === true
        || value === false
    ) {
        return value;
    }

    if (typeof(value) == "object") {

        let copyMethod = value[cocktail.ui.COPY_VALUE];

        if (copyMethod) {
            return copyMethod.call(value);
        }
        else {
            return Object.assign({}, value);
        }
    }

    return value;
}

Date.prototype[cocktail.ui.COPY_VALUE] = function () {
    return new Date(this);
}

RegExp.prototype[cocktail.ui.COPY_VALUE] = function () {
    return new RegExp(this);
}

Array.prototype[cocktail.ui.COPY_VALUE] = function () {
    let copy = [];
    for (let item of this) {
        copy.push(cocktail.ui.copyValue(item));
    }
    return copy;
}

Set.prototype[cocktail.ui.COPY_VALUE] = function () {
    let copy = new Set();
    for (let item of this) {
        copy.add(cocktail.ui.copyValue(item));
    }
    return copy;
}

Map.prototype[cocktail.ui.COPY_VALUE] = function () {
    let copy = new Map();
    for (let item of this) {
        copy.set(
            cocktail.ui.copyValue(item[0]),
            cocktail.ui.copyValue(item[1])
        );
    }
    return copy;
}

