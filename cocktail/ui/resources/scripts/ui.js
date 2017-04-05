/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2016
-----------------------------------------------------------------------------*/

cocktail.declare("cocktail.ui");

cocktail.ui.OBSERVED_ATTRIBUTES = Symbol("cocktail.ui.OBSERVED_ATTRIBUTES");

cocktail.ui.component = function (params) {

    params.tag = params.fullName.replace(/\./g, "-").toLowerCase();

    if (params.decorators) {
        if (!params.properties) {
            params.properties = {};
        }
        for (let decorator of params.decorators) {
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
            cocktail.ui.property(cls, propName, params.properties[propName]);
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

cocktail.ui.trigger = function (obj, eventType, detail = null) {
    obj.dispatchEvent(new CustomEvent(eventType, {detail: detail}));
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

cocktail.ui.propertyIsChanging = function (instance, propertyName) {
    return instance.constructor[propertyName]._changingInstances.has(instance);
}

cocktail.ui.property = function (component, name, options = null) {

    // Add a static object to the class constructor to provide access to symbols
    // and metadata used by the property
    let meta = {
        name: name,
        component: component,
        GET: Symbol(`${component.fullName}.${name}.GET`),
        SET: Symbol(`${component.fullName}.${name}.SET`),
        VALUE: Symbol(`${component.fullName}.${name}.VALUE`),
        reflected: options && options.reflected || false,
        eventName: name + "Changed",
        getType: function (obj) {
            return (typeof(this.type) == "function") ? this.type(obj) : this.type;
        }
    };

    // Determine the type of the property (used in attribute serialization /
    // deserialization)
    if (options) {
        meta.type = options.type;
        if (typeof(meta.type) == "string") {
            meta.type = cocktail.ui.property.types[meta.type];
        }
    }

    if (!meta.type) {
        meta.type = cocktail.ui.property.types.string;
    }

    // Keep a set of weak references to component instances whose value is
    // being modified. Useful to prevent infinite recursion in property -
    // attribute reflection and bidirectionally interlocked properties.
    Object.defineProperty(meta, "_changingInstances", {
        value: new WeakSet(),
        enumerable: false,
        configurable: false
    });

    // Property getter
    let descriptorGetter = function () {
        let getter = this[meta.GET];
        if (getter) {
            return getter.call(this);
        }
        else {
            return this[meta.VALUE];
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

            // Keep track of which instances are being changed
            try {
                meta._changingInstances.add(this);

                // Set the new value
                let setter = this[meta.SET];
                if (setter) {
                    setter.call(this, value);
                }
                else {
                    this[meta.VALUE] = value;
                }

                // Track value changes
                let newValue = this[name];
                if (newValue !== oldValue) {

                    // Reflect the property's value to its DOM attribute
                    if (meta.reflected) {
                        this.setAttribute(name, meta.getType(this).serializeValue(newValue));
                    }

                    // Trigger a changed event
                    cocktail.ui.trigger(this, meta.eventName, {
                        oldValue: oldValue,
                        newValue: newValue
                    });
                }
            }
            finally {
                meta._changingInstances.delete(this);
            }
        }
    }

    // Enable attribute observation for properties with attribute reflection
    // enabled
    if (meta.reflected) {
        meta.attributeName = name.toLowerCase();
        component[cocktail.ui.OBSERVED_ATTRIBUTES].push(meta.attributeName);
    }

    // Install the given getter and setter methods
    let getterImpl = options && options.get;
    if (getterImpl) {
        component.prototype[meta.GET] = getterImpl;
    }

    let setterImpl = options && options.set;
    if (setterImpl) {
        component.prototype[meta.SET] = setterImpl;
    }

    // Attach the property to the component
    component[name] = meta;
    component["_attr_" + name.toLowerCase()] = meta;
    Object.defineProperty(component.prototype, name, {
        get: descriptorGetter,
        set: descriptorSetter,
        enumerable: true
    });
}

cocktail.ui.property.types = {
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
            root = this.attachShadow({mode: "open"});
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
        if (property && property.reflected && !property._changingInstances.has(this)) {
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

