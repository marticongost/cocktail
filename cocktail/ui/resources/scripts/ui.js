/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2016
-----------------------------------------------------------------------------*/

cocktail.declare("cocktail.ui");

for (let key of ["INITIALIZE", "ADD", "COMPONENT", "COMPONENTS", "ID", "OWNER"]) {
    cocktail.ui[key] = Symbol("cocktail.ui." + key);
}

cocktail.ui._root = function (component, element) {
    if (typeof(element) == "string") {
        element = document.createElement(element);
    }
    element[cocktail.ui.COMPONENT] = component;
    let set = element[cocktail.ui.COMPONENTS];
    if (set === undefined) {
        set = new Set([component]);
        element[cocktail.ui.COMPONENTS] = set;
    }
    else {
        set.add(component);
    }
    element.classList.add(component.cssClassName);
    component.setInstanceMembers(element);
    return element;
}

cocktail.ui._elem = function (owner, partId, element) {
    if (typeof(element) == "string") {
        element = document.createElement(element);
    }
    let component = owner[cocktail.ui.COMPONENT];
    if (partId) {
        owner[partId] = element;
    }
    element.classList.add(component.cssClassName + "-" + partId);
    element[cocktail.ui.ID] = partId;
    element[cocktail.ui.OWNER] = owner;
    return element;
}

cocktail.ui.add = function (parentNode, child) {
    let method = parentNode[cocktail.ui.ADD];
    if (method) {
        method.call(parentNode, child);
    }
    else {
        parentNode.appendChild(child);
    }
}

cocktail.ui.insertTranslation = function (element, key) {
    let text = cocktail.ui.translations[key];
    if (text) {
        element.appendChild(document.createTextNode(text));
    }
}

cocktail.ui.trigger = function (obj, eventType, detail = null) {
    obj.dispatchEvent(new CustomEvent(eventType, {detail}));
}

cocktail.ui.isInstance = function (element, component) {
    let set = element[cocktail.ui.COMPONENTS];
    return set !== undefined && set.has(component);
}

cocktail.ui.closestInstance = function (element, component) {
    do {
        if (cocktail.ui.isInstance(element, component)) {
            return element;
        }
        element = element.parentNode;
    }
    while (element);
}

/* Components
-----------------------------------------------------------------------------*/
cocktail.ui.Component = {
    extend(fullName, createInstance, parentComponent = null) {
        let component = function () {
            let instance = createInstance.call(component);
            let initializer = instance[cocktail.ui.INITIALIZE];
            if (initializer) {
                initializer.call(instance);
            }
            return instance;
        }
        cocktail.setVariable(fullName, component);
        component.__proto__ = this;
        component.createInstance = createInstance;
        component.baseComponent = this;
        component.parentComponent = parentComponent;
        component.instanceMembers = {};
        component.fullName = fullName;
        component.cssClassName = fullName.replace(/\./g, "-");

        if (parentComponent) {
            let name = fullName.substr(fullName.lastIndexOf(".") + 1);
            parentComponent.instanceMembers[name] = component;
        }

        return component;
    },
    define(members) {
        for (let key of Reflect.ownKeys(members)) {
            let value = members[key];
            if (value instanceof cocktail.ui.ComponentMember) {
                value.attach(this, key);
            }
            else {
                this.instanceMembers[key] = value;
            }
        }
    },
    *iterInheritance() {
        let component = this;
        while (component) {
            yield component;
            component = component.baseComponent;
        }
    },
    setInstanceMembers(instance) {
        if (this.instanceMembers) {
            for (let key of Reflect.ownKeys(this.instanceMembers)) {
                let value = this.instanceMembers[key];
                if (value instanceof cocktail.ui.ComponentMember) {
                    value.initInstance(instance);
                }
                else {
                    instance[key] = value;
                }
            }
        }
    }
}

/* Component members
-----------------------------------------------------------------------------*/
cocktail.ui.ComponentMember = class ComponentMember {

    attach(component, key) {
        component.instanceMembers[key] = this;
        this.component = component;
        this.key = key;
    }

    initInstance(instance) {}
}

/* Component accessors
-----------------------------------------------------------------------------*/
cocktail.ui.Accessor = class Accessor extends cocktail.ui.ComponentMember {

    setAccessorMethods(params = null) {
        if (!params || params.get === undefined) {
            this.get = this.getValue;
        }
        else {
            this.get = params.get;
        }

        if (!params || params.set === undefined) {
            this.set = this.setValue;
        }
        else {
            this.set = params.set;
        }
    }

    initInstance(instance) {
        let accessor = this;
        let dfn = {
            enumerable: true,
            get: function () {
                return accessor.get(this);
            }
        };
        if (this.set !== null) {
            dfn.set = function (value) {
                accessor.set(this, value);
            };
        }
        Object.defineProperty(instance, this.key, dfn);
    }

    getValue(obj) {}
    setValue(obj, value) {}
}

/* Component properties
-----------------------------------------------------------------------------*/
cocktail.ui.Property = class Property extends cocktail.ui.Accessor {

    constructor(params = null) {
        super(params);
        this.symbol = Symbol();
        this.getDefault = params && params.getDefault;
        this.setAccessorMethods(params);
    }

    getValue(obj) {
        let value = obj[this.symbol];
        if (value === undefined) {
            value = this.getDefault ? this.getDefault(obj) : this.defaultValue;
            obj[this.symbol] = obj;
        }
        return value;
    }

    setValue(obj, value, triggerEvent = true) {
        let prevValue = this.getValue(obj);
        obj[this.symbol] = value;
        if (triggerEvent && value != prevValue) {
            cocktail.ui.trigger(
                    obj,
                    this.key + "Changed",
                    {previous: prevValue, value: value}
                    );
        }
    }
}

cocktail.ui.Property.prototype.defaultValue = null;

/* Component attributes
-----------------------------------------------------------------------------*/
cocktail.ui.Attribute = class Attribute extends cocktail.ui.Accessor {

    constructor(params) {
        super();
        this.setAccessorMethods(params);
    }

    attach(component, key) {
        super.attach(component, key);
        this.attributeName = `data-${key.toLowerCase()}`;
    }

    getValue(obj) {
        let value = obj.getAttribute(this.attributeName);
        if (value !== null) {
            value = this.parseValue(value);
        }
        return value;
    }

    setValue(obj, value, triggerEvent = true) {
        let prevValue = this.getValue(obj);
        obj.setAttribute(this.attributeName, this.serializeValue(value));
        if (triggerEvent && value != prevValue) {
            cocktail.ui.trigger(
                    obj,
                    this.key + "Changed",
                    {previous: prevValue, value: value}
                    );
        }
    }

    parseValue(value) {
        return value;
    }

    serializeValue(value) {
        return String(value);
    }
}

/* String attributes
-----------------------------------------------------------------------------*/
cocktail.ui.StringAttribute = class StringAttribute extends cocktail.ui.Attribute {

    constructor(params) {
        super();
        this.setAccessorMethods(params);
    }
}

/* Boolean attributes
-----------------------------------------------------------------------------*/
cocktail.ui.BooleanAttribute = class BooleanAttribute extends cocktail.ui.Attribute {

    constructor(params) {
        super();
        this.setAccessorMethods(params);
    }

    parseValue(value) {
        if (value === "true") {
            return true;
        }
        else if (value == "false") {
            return false;
        }
        else {
            return undefined;
        }
    }
}


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
cocktail.ui.dataBound = function (component) {
    component.define(cocktail.ui.dataBound.componentProperties);
}

cocktail.ui.dataBound.componentProperties = {
    dataSource: new cocktail.ui.Property(),
    dataState: new cocktail.ui.StringAttribute()
}

cocktail.ui.DISPLAY = Symbol("cocktail.ui.DISPLAY");

