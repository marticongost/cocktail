/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2016
-----------------------------------------------------------------------------*/

cocktail.declare("cocktail.ui");

cocktail.ui.OBSERVED_ATTRIBUTES = Symbol("cocktail.ui.OBSERVED_ATTRIBUTES");

cocktail.ui.ComponentError = class ComponentError {

    constructor(message) {
        this.message = message;
    }

    toString() {
        return this.message;
    }
}

cocktail.ui.component = function (params) {

    params.tag = params.fullName.replace(/\./g, "-").toLowerCase();

    if (params.decorators) {
        if (!params.properties) {
            params.properties = {};
        }
        for (let decorator of params.decorators) {
            if (!decorator) {
                console.log(params);
                throw new cocktail.ui.ComponentError(
                    `Component ${params.fullName} references an inexistent decorator`
                );
            }
            decorator(params);
        }
    }

    let cls = params.cls;
    cls.fullName = params.fullName;
    cls.tag = params.tag;
    cls.parentComponent = params.parentComponent;
    cls.baseTag = params.baseTag;
    cls[cocktail.ui.OBSERVED_ATTRIBUTES] = [];
    cocktail.setVariable(params.fullName, cls);

    if (params.properties) {
        for (let propName in params.properties) {
            new cocktail.ui.Property(cls, propName, params.properties[propName]);
        }
    }

    if (cls.baseTag) {
        customElements.define(cls.tag, cls, {extends: cls.baseTag});
    }
    else {
        customElements.define(cls.tag, cls);
    }

    return cls;
}

cocktail.ui._getObservedAttributes = function (cls) {
    let attributes = [];
    let clsAttributes;
    while (cls) {
        clsAttributes = cls[cocktail.ui.OBSERVED_ATTRIBUTES];
        if (clsAttributes) {
            attributes.push(...clsAttributes);
        }
        cls = Object.getPrototypeOf(cls);
    }
    return attributes;
}

cocktail.ui.getShadow = function (element) {
    return element.shadowRoot || element.getRootNode();
}

cocktail.ui.insertTranslation = function (element, key) {
    let text = cocktail.ui.translations[key];
    if (text) {
        element.appendChild(document.createTextNode(text));
    }
}

cocktail.ui.empty = function (element) {
    let child;
    while (child = element.lastChild) {
        element.removeChild(child);
    }
}

cocktail.ui.trigger = function (obj, eventType, detail = null, options = null) {
    if (!options) {
        options = {};
    }
    options.detail = detail;
    obj.dispatchEvent(new CustomEvent(eventType, options));
}

cocktail.ui.isInstance = function (element, component) {
    let set = element[cocktail.ui.COMPONENTS];
    return set !== undefined && set.has(component);
}

cocktail.ui.closestInstance = function (element, component) {
    do {
        if (element instanceof component) {
            return element;
        }
        element = element.parentNode || element.host;
    }
    while (element);
}

cocktail.ui.isComponent = function (obj) {
    return Boolean(
        typeof(obj) == "function"
        && obj.prototype instanceof HTMLElement
        && obj.fullName
    );
}

cocktail.ui.createDisplay = function (display, context) {
    let element = cocktail.ui.isComponent(display) ? display.create() : display();
    Object.assign(element, context);
    return element;
}

{
    const LINKS = Symbol("cocktail.ui.LINKS");

    let setLink = function (source, target, property, synchronization) {

        let links = source[LINKS];
        if (links === undefined) {
            links = new Map();
            source[LINKS] = links;
        }

        let propertyLinks = links.get(property);
        if (propertyLinks === undefined) {
            propertyLinks = new Map();
            links.set(property, propertyLinks);
        }

        propertyLinks.set(target, synchronization);
    }

    let clearLink = function (source, target, property) {

        let links = source[LINKS];
        if (links !== undefined) {
            let propertyLinks = links.get(property);
            if (propertyLinks !== undefined) {
                propertyLinks.delete(target);
                if (!propertyLinks.size) {
                    links.delete(property);
                    if (!links.size) {
                        delete source[LINKS];
                    }
                }
            }
        }
    }

    cocktail.ui.link = function (source, target, property, exporter = null, importer = null, initialize = true) {

        let sourceProperty, targetProperty;

        if (property instanceof Array) {
            [sourceProperty, targetProperty] = property;
        }
        else {
            sourceProperty = property;
            targetProperty = property;
        }

        if (sourceProperty instanceof cocktail.ui.Property) {
            sourceProperty = sourceProperty.name;
        }

        if (targetProperty instanceof cocktail.ui.Property) {
            targetProperty = targetProperty.name;
        }

        let exportSync = exporter ? {customSync: exporter} : {property: targetProperty};
        let importSync = importer ? {customSync: importer} : {property: sourceProperty};

        setLink(source, target, sourceProperty, exportSync);
        setLink(target, source, targetProperty, importSync);

        // Set the initial value
        if (initialize) {
            exportSync.running = true;
            try {
                if (exporter) {
                    exporter(source, target);
                }
                else {
                    target[targetProperty] = source[sourceProperty];
                }
            }
            finally {
                exportSync.running = false;
            }
        }
    }

    cocktail.ui.removeLink = function (source, target, synchronization) {

        let sourceProperty, targetProperty;

        if (typeof(synchronization) == "string") {
            sourceProperty = synchronization;
            targetProperty = synchronization;
        }
        else if (synchronization instanceof cocktail.ui.Property) {
            sourceProperty = synchronization.name;
            targetProperty = synchronization.name;
        }
        else {
            sourceProperty = synchronization.sourceProperty;
            if (sourceProperty instanceof cocktail.ui.Property) {
                sourceProperty = sourceProperty.name;
            }

            targetProperty = synchronization.targetProperty;
            if (targetProperty instanceof cocktail.ui.Property) {
                targetProperty = targetProperty.name;
            }
        }

        clearLink(source, target, sourceProperty);
        clearLink(target, source, targetProperty);
    }

    let PROPERTY_COMPONENT = Symbol("cocktail.ui.PROPERTY_COMPONENT");
    let PROPERTY_NAME = Symbol("cocktail.ui.PROPERTY_NAME");
    let PROPERTY_TYPE = Symbol("cocktail.ui.PROPERTY_TYPE");
    let PROPERTY_GET = Symbol("cocktail.ui.PROPERTY_GET");
    let PROPERTY_SET = Symbol("cocktail.ui.PROPERTY_SET");
    let PROPERTY_VALUE = Symbol("cocktail.ui.PROPERTY_VALUE");
    let PROPERTY_REFLECTED = Symbol("cocktail.ui.PROPERTY_REFLECTED");
    let PROPERTY_IS_FINAL = Symbol("cocktail.ui.PROPERTY_IS_FINAL");
    let PROPERTY_EVENT_OPTIONS = Symbol("cocktail.ui.PROPERTY_EVENT_OPTIONS");
    let PROPERTY_NORMALIZATION = Symbol("cocktail.ui.PROPERTY_NORMALIZATION");
    let PROPERTY_CHANGED_CALLBACK = Symbol("cocktail.ui.PROPERTY_CHANGED_CALLBACK");
    let PROPERTY_CHANGING_INSTANCES = Symbol("cocktail.ui.PROPERTY_CHANGING_INSTANCES");

    cocktail.ui.Property = class Property {

        constructor(component, name, options = null) {

            let property = this;

            this[PROPERTY_COMPONENT] = component;
            this[PROPERTY_NAME] = name;
            this[PROPERTY_GET] = Symbol(`${component.fullName}.${name}.GET`);
            this[PROPERTY_SET] = Symbol(`${component.fullName}.${name}.SET`);
            this[PROPERTY_VALUE] = Symbol(`${component.fullName}.${name}.VALUE`);
            this[PROPERTY_REFLECTED] = options && options.reflected || false;
            this[PROPERTY_IS_FINAL] = options && options.isFinal || false;
            this[PROPERTY_EVENT_OPTIONS] = {
                composed: options && options.eventIsComposed,
                bubbles: options && options.eventBubbles
            }
            this[PROPERTY_NORMALIZATION] = options && options.normalization;
            this[PROPERTY_CHANGED_CALLBACK] = options && options.changedCallback;

            // Determine the type of the property (used in attribute serialization /
            // deserialization)
            let type;
            if (options) {
                type = options.type;
                if (typeof(type) == "string") {
                    type = cocktail.ui.Property.types[type];
                }
            }

            if (!type) {
                type = cocktail.ui.Property.types.string;
            }

            this[PROPERTY_TYPE] = type;

            // Keep a set of weak references to component instances whose value is
            // being modified. Useful to prevent infinite recursion in property -
            // attribute reflection and bidirectionally interlocked properties.
            this[PROPERTY_CHANGING_INSTANCES] = new WeakSet();

            // Property getter
            let descriptorGetter = function () {
                let getter = this[property[PROPERTY_GET]];
                if (getter) {
                    return getter.call(this);
                }
                else {
                    return this[property[PROPERTY_VALUE]];
                }
            }

            // Property setter
            let descriptorSetter = null;
            if (options && options.set === null) {
                descriptorSetter = undefined; // read-only property
            }
            else {
                descriptorSetter = function (value) {
                    let oldValue = this[name];

                    if (oldValue !== undefined && property[PROPERTY_IS_FINAL]) {
                        throw new cocktail.ui.FinalPropertyChangedError(property);
                    }

                    // Keep track of which instances are being changed
                    try {
                        property[PROPERTY_CHANGING_INSTANCES].add(this);

                        // Normalization
                        let normalization = property[PROPERTY_NORMALIZATION];
                        if (normalization) {
                            value = normalization.call(this, value);
                        }

                        // Set the new value
                        let setter = this[property.SET];
                        if (setter) {
                            setter.call(this, value);
                        }
                        else {
                            this[property[PROPERTY_VALUE]] = value;
                        }

                        // Track value changes
                        let newValue = this[name];
                        if (newValue !== oldValue) {

                            // Reflect the property's value to its DOM attribute
                            if (property[PROPERTY_REFLECTED]) {
                                this.setAttribute(name, property.getType(this).serializeValue(newValue));
                            }

                            // Change callback
                            let changedCallback = property[PROPERTY_CHANGED_CALLBACK];
                            if (changedCallback) {
                                changedCallback.call(this, oldValue, newValue);
                            }

                            // Trigger a changed event
                            cocktail.ui.trigger(
                                this,
                                property.eventName,
                                {oldValue: oldValue, newValue: newValue},
                                property.eventOptions
                            );

                            // Propagate the change to linked properties
                            let links = this[LINKS];
                            if (links) {
                                let propertyLinks = links.get(name);
                                if (propertyLinks) {
                                    for (let [linkedTarget, synchronization] of propertyLinks.entries()) {
                                        if (!synchronization.running) {
                                            synchronization.running = true;
                                            try {
                                                if (synchronization.customSync) {
                                                    synchronization.customSync(this, linkedTarget);
                                                }
                                                else {
                                                    linkedTarget[synchronization.property] = newValue;
                                                }
                                            }
                                            finally {
                                                synchronization.running = false;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    finally {
                        property[PROPERTY_CHANGING_INSTANCES].delete(this);
                    }
                }
            }

            // Enable attribute observation for properties with attribute reflection
            // enabled
            if (this[PROPERTY_REFLECTED]) {
                component[cocktail.ui.OBSERVED_ATTRIBUTES].push(this.attributeName);
            }

            // Install the given getter and setter methods
            let getterImpl = options && options.get;
            if (getterImpl) {
                component.prototype[this[PROPERTY_GET]] = getterImpl;
            }

            let setterImpl = options && options.set;
            if (setterImpl) {
                component.prototype[this[PROPERTY_SET]] = setterImpl;
            }

            // Attach the property to the component
            component[name] = this;
            component["_attr_" + name.toLowerCase()] = property;
            Object.defineProperty(component.prototype, name, {
                get: descriptorGetter,
                set: descriptorSetter,
                enumerable: true
            });
        }

        get component() {
            return this[PROPERTY_COMPONENT];
        }

        get name() {
            return this[PROPERTY_NAME];
        }

        get type() {
            return this[PROPERTY_TYPE];
        }

        get GET() {
            return this[PROPERTY_GET];
        }

        get SET() {
            return this[PROPERTY_SET];
        }

        get VALUE() {
            return this[PROPERTY_VALUE];
        }

        get reflected() {
            return this[PROPERTY_REFLECTED];
        }

        get isFinal() {
            return this[PROPERTY_IS_FINAL];
        }

        get attributeName() {
            return this[PROPERTY_NAME].toLowerCase();
        }

        get eventName() {
            return this[PROPERTY_NAME] + "Changed";
        }

        get eventOptions() {
            return this[PROPERTY_EVENT_OPTIONS];
        }

        get normalization() {
            return this[PROPERTY_NORMALIZATION];
        }

        get changedCallback() {
            return this[PROPERTY_CHANGED_CALLBACK];
        }

        toString() {
            return `Property(${this.component.fullName}.${this.name})`;
        }

        getType(obj) {
            let type = this[PROPERTY_TYPE];
            return (typeof(type) == "function") ? type(obj) : type;
        }

        isChanging(instance) {
            return this[PROPERTY_CHANGING_INSTANCES].has(instance);
        }
    }
}

cocktail.ui.Property.types = {
    string: {
        serializeValue(value) {
            return String(value);
        },
        parseValue(value) {
            return value;
        }
    },
    number: {
        serializeValue(value) {
            return String(value);
        },
        parseValue(value) {
            return Number(value);
        }
    },
    boolean: {
        serializeValue(value) {
            return value ? "true" : "false";
        },
        parseValue(value) {
            if (value == "true") {
                return true;
            }
            else if (value == "false") {
                return false;
            }
            else {
                return undefined;
            }
        }
    },
    identifiers: {
        serializeValue(value) {
            if (value instanceof Set) {
                value = [...value];
            }
            return value ? value.join(" ") : "";
        },
        parseValue(value) {
            return new Set(value.split(/\s+/g));
        }
    }
}

cocktail.ui.FinalPropertyChangedError = class FinalPropertyChangedError {

    constructor(property) {
        this.property = property;
    }

    toString() {
        return `${this.property} has been marked as being final, but its value has been changed.`;
    }
}

cocktail.ui.componentStaticMembers = {
    embeddedStyles: null,
    create(properties = null) {
        let instance;
        if (this.baseTag) {
            instance = document.createElement(this.baseTag, {is: this.tag});
        }
        else {
            instance = new this();
        }
        instance.initialize();
        if (properties) {
            Object.assign(instance, properties);
        }
        return instance;
    }
}

cocktail.ui.componentMembers = {
    initialize() {

        let root;

        if (this.constructor.parentComponent) {
            root = this;
        }
        else {
            root = this.attachShadow({
                mode: "open",
                delegatesFocus: this.constructor.delegatesFocus
            });
        }

        // Linked CSS
        for (let uri of this.constructor.linkedStyleSheets) {
            let link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = uri;
            root.appendChild(link);
        }

        // Embedded CSS
        let css = this.constructor.embeddedStyles;
        if (css) {
            let styles = document.createElement('style');
            styles.type = 'text/css';
            styles.textContent = css;
            root.appendChild(styles);
        }
    },
    attributeChangedCallback(attrName, oldValue, newValue) {
        let property = this.constructor["_attr_" + attrName];
        if (property && property.reflected && !property.isChanging(this)) {
            this[property.name] = property.getType(this).parseValue(newValue);
        }
    }
}

cocktail.ui.base = new Proxy({}, {
    get: function (target, name) {
        let cls = target[name];
        if (!cls) {
            let iface = window[name];
            if (!iface) {
                throw "Unknown HTML element interface: " + name;
            }
            cls = class extends iface {};
            cls.linkedStyleSheets = [];
            Object.assign(cls, cocktail.ui.componentStaticMembers);
            Object.assign(cls.prototype, cocktail.ui.componentMembers);
            target[name] = cls;
        }
        return cls;
    }
});

