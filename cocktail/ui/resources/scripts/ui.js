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
        GET: Symbol(`${component.fullName}.${name}.GET`),
        SET: Symbol(`${component.fullName}.${name}.SET`),
        VALUE: Symbol(`${component.fullName}.${name}.VALUE`),
        reflected: options && options.reflected || false,
        eventName: name + "Changed"
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
                        this.setAttribute(name, meta.type.serialize(newValue));
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
        component[cocktail.ui.OBSERVED_ATTRIBUTES].push(name);
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
    Object.defineProperty(component.prototype, name, {
        get: descriptorGetter,
        set: descriptorSetter,
        enumerable: true
    });
}

cocktail.ui.property.types = {
    string: {
        serialize(value) {
            return String(value);
        },
        parse(value) {
            return value;
        }
    },
    number: {
        serialize(value) {
            return String(value);
        },
        parse(value) {
            return Number(value);
        }
    },
    boolean: {
        serialize(value) {
            return value ? "true" : "false";
        },
        parse(value) {
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
        serialize(value) {
            if (value instanceof Set) {
                value = [...value];
            }
            return value ? value.join(" ") : "";
        },
        parse(value) {
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
        let propertyMeta = this.constructor[attrName];
        if (propertyMeta && propertyMeta.reflected && !propertyMeta._changingInstances.has(this)) {
            this[attrName] = propertyMeta.type.parse(newValue);
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

/* Requests
-----------------------------------------------------------------------------*/
cocktail.ui.request = function (params) {

    let xhr = new XMLHttpRequest();

    let promise = new Promise(function (resolve, reject) {

        xhr.onload = function () {
            resolve(xhr);
        }

        xhr.onerror = function () {
            reject(xhr);
        }

        xhr.open(params.method || "GET", params.url);

        let data = params.data;
        let headers = params.headers || {};

        if (typeof(data) == "object") {
            data = JSON.stringify(data);
            headers["Content-Type"] = "application/json";
        }

        for (let key in headers) {
            xhr.setRequestHeader(key, headers[key]);
        }

        if (params.responseType) {
            xhr.responseType = params.responseType;
        }

        if (cocktail.csrfprotection) {
            cocktail.csrfprotection.setupRequest(xhr);
        }

        xhr.send(data);
    });

    promise.xhr = xhr;
    return promise;
}

/* Data sources
-----------------------------------------------------------------------------*/
cocktail.ui.DataSource = class DataSource {

    constructor(parameters = null) {
    }

    load(parameters = null) {}

    getValue(object, member, language = null) {
        let value = object[member.name];
        if (member.translated && language) {
            return value ? value[language] : null;
        }
        else {
            return value;
        }
    }
}

/* HTTPDataSource
-----------------------------------------------------------------------------*/
cocktail.ui.HTTPDataSource = class HTTPDataSource extends cocktail.ui.DataSource {

    constructor(parameters = null) {
        super(parameters);
        if (parameters) {
            this.url = parameters.url;
        }
    }

    getRequestParameters(parameters = null) {
        if (!parameters) {
            parameters = {};
        }
        parameters.url = this.url;
        parameters.responseType = "json";
        return parameters;
    }

    load(parameters = null) {

        parameters = this.getRequestParameters(parameters);

        return new Promise(function (resolve, reject) {
            cocktail.ui.request(parameters)
                .then(function (request) {
                    resolve(request.response);
                })
                .catch(function (e) {
                    reject(e);
                });
        });
    }
}

/* Data binding
-----------------------------------------------------------------------------*/
cocktail.ui.dataBound = function (registration) {
    registration.properties["dataSource"] = {};
    registration.properties["dataState"] = {reflected: true};
}

cocktail.ui.DISPLAY = Symbol("cocktail.ui.DISPLAY");

