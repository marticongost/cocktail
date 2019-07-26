/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         November 2016
-----------------------------------------------------------------------------*/

cocktail.declare("cocktail.ui");

// Custom formatters for the Chrome console
cocktail.ui.CONSOLE_HEADER = Symbol("cocktail.ui.CONSOLE_HEADER");
cocktail.ui.CONSOLE_CHILDREN = Symbol("cocktail.ui.CONSOLE_CHILDREN");

if (!window.devtoolsFormatters) {
    window.devtoolsFormatters = [];
}

devtoolsFormatters.push({
    header: function (obj) {
        var formatter = obj[cocktail.ui.CONSOLE_HEADER];
        if (formatter) {
            return formatter.call(obj);
        }
        return null;
    },
    hasBody: function () {
        return true;
    },
    body: function (obj, config) {

        let children;

        if (obj[cocktail.ui.CONSOLE_CHILDREN]) {
            children = obj[cocktail.ui.CONSOLE_CHILDREN](config);
        }
        else {
            children = [];
            for (let key in obj) {
                children.push([key, obj[key]]);
            }
        }

        const elements = [];

        for (let [key, value] of children) {

            let child;
            const type = typeof(value);

            if (value === undefined) {
                continue;
            }

            if (type == "object") {
                if (value instanceof cocktail.ui.ConsoleMarkup) {
                    child = value.markup;
                }
                else {
                    child = [
                        "object", {
                            object: value,
                            config: {
                                key: key,
                                cocktailKeyFormatter: true
                            }
                        }
                    ];
                }
            }
            else if (type == "number" || type == "boolean") {
                child = ["span", {style: "color: #4730b5"}, value.toString()];
            }
            else if (type == "string") {
                child = [
                    "span",
                    '"',
                    ["span", {style: "color: #c0272c"}, value.toString()],
                    '"'
                ];
            }
            else {
                child = String(value);
            }

            elements.push([
                "div", {},
                ["span", {style: "color: #8b0b93"}, key],
                ": ",
                child
            ]);
        }

        return ["div", {}].concat(elements);
    }
});

cocktail.ui.ConsoleMarkup = class ConsoleMarkup {

    constructor(...markup) {
        this.markup = markup;
    }
}

// Splash screen
cocktail.ui.SPLASH_HIDE_DELAY = 500;

cocktail.ui.splash = function (splash, mainComponent) {

    mainComponent.main(splash.container);
    document.body.appendChild(splash);

    window.addEventListener("load", () => {
        window.setTimeout(
            () => { splash.stage = "loaded"; },
            cocktail.ui.SPLASH_HIDE_DELAY
        );
    });

    splash.container.addEventListener("animationend", () => {
        splash.stage = "hidden";
    });
}

// Component declaration
{
    let uiPrepared;
    cocktail.ui.rootReady = new Promise((resolve, reject) => { uiPrepared = resolve; });

    const OBSERVED_ATTRIBUTES = Symbol("cocktail.ui.OBSERVED_ATTRIBUTES");
    const IS_COMPONENT = Symbol("cocktail.ui.IS_COMPONENT");
    const TYPES_SCOURED_FOR_PROPERTIES = new WeakSet();
    let globalStyleSheet = null;
    let globalStyleSheetResolved = false;

    cocktail.ui.component = function (parameters) {

        let cls = parameters.cls;
        cls.fullName = parameters.fullName;
        cls.tag = parameters.fullName.replace(/\./g, "-").toLowerCase();
        cls.parentComponent = parameters.parentComponent;
        cls.baseTag = parameters.baseTag || cls.baseTag;
        cls[OBSERVED_ATTRIBUTES] = [];

        cocktail.setVariable(parameters.fullName, cls);

        // Property declaration
        let declareProperties = function (type) {

            let base = Object.getPrototypeOf(type);
            if (base && !TYPES_SCOURED_FOR_PROPERTIES.has(base)) {
                declareProperties(base);
            }

            let properties = type.componentProperties;
            if (properties) {
                for (let propName in properties) {
                    new cocktail.ui.Property(cls, propName, properties[propName]);
                }
            }
            TYPES_SCOURED_FOR_PROPERTIES.add(type);
        }
        declareProperties(cls);

        // Component registration
        if (cls.baseTag) {
            customElements.define(cls.tag, cls, {extends: cls.baseTag});
        }
        else {
            customElements.define(cls.tag, cls);
        }

        return cls;
    }

    const OBSERVED_OBJECTS = Symbol("cocktail.ui.Observer.OBSERVED_OBJECTS");
    const OBSERVERS = Symbol("cocktail.ui.Observable.OBSERVERS");

    cocktail.ui.invalidationInProgress = false;

    cocktail.ui.observer = (cls) => class Observer extends (cls) {

        observe(observable) {

            let observedObjects = this[OBSERVED_OBJECTS];
            if (observedObjects === undefined) {
                observedObjects = new Set();
                this[OBSERVED_OBJECTS] = observedObjects;
            }
            observedObjects.add(observable);

            let observers = observable[OBSERVERS]
            if (observers === undefined) {
                observers = new Set();
                observable[OBSERVERS] = observers;
            }
            observers.add(this);
        }

        stopObserving(observable) {
            let observedObjects = this[OBSERVED_OBJECTS];
            if (observedObjects !== undefined) {
                observedObjects.delete(observable);
                observable[OBSERVERS].delete(this);
            }
        }

        stopAllObservation() {
            let observedObjects = this[OBSERVED_OBJECTS];
            if (observedObjects) {
                for (let observable of observedObjects) {
                    observable[OBSERVERS].delete(this);
                }
                observedObjects.clear();
            }
        }

        invalidation(changes) {
        }
    }

    cocktail.ui.Observable = class Observable {

        *iterObservers() {
            let observers = this[OBSERVERS];
            if (observers) {
                for (let observer of observers) {
                    yield observer;
                }
            }
        }

        trigger(change) {
            change.source = this;
            const observers = this[OBSERVERS];
            if (observers) {
                const invalidationWasAlreadyInProgress = cocktail.ui.invalidationInProgress;
                cocktail.ui.invalidationInProgress = true;
                try {
                    for (let observer of this[OBSERVERS]) {
                        observer.invalidation(change);
                    }
                }
                finally {
                    cocktail.ui.invalidationInProgress = invalidationWasAlreadyInProgress;
                }
            }
        }
    }

    const WINDOW_LISTENERS = Symbol("cocktail.ui.ComponentBase.WINDOW_LISTENERS");

    let componentBase = (cls) => class ComponentBase extends cocktail.ui.observer(cls) {

        static [cocktail.ui.CONSOLE_HEADER]() {

            const pos = this.fullName.lastIndexOf(".");
            const ns = this.fullName.substr(0, pos + 1);
            const name = this.fullName.substr(pos + 1);

            return [
                "div", {style: "color: #842597"},
                ns,
                ["span", {style: "font-weight: bold"}, name]
            ];
        }

        static get [IS_COMPONENT]() {
            return true;
        }

        static get requiresShadowDOM() {
            return false;
        }

        static main(container) {
            let instance = this.create();
            cocktail.ui.root = instance;
            container.appendChild(instance);
            uiPrepared(instance);
        }

        static create(properties = null) {
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

        static withProperties(properties) {
            return {
                create: (extraProperties = null) => this.create(Object.assign({}, properties, extraProperties))
            };
        }

        static *iterComponentInheritance() {
            let proto = Object.getPrototypeOf(this);
            while (proto !== ComponentBase) {
                yield proto;
                proto = Object.getPrototypeOf(proto);
            }
        }

        initialize() {

            let root;

            // Subcomponents don't get their own, unless they are based on a custom
            // component
            if (this.constructor.requiresShadowDOM) {
                try {
                    root = this.attachShadow({
                        mode: "open",
                        delegatesFocus: this.constructor.delegatesFocus
                    });
                }
                catch (e) {
                    throw `Error creating the shadow DOM root on a <${this.tagName}> element for the ${this.constructor.fullName} component`;
                }
            }
            else {
                root = this;
            }

            // Linked CSS
            let linkedSheets = this.constructor.linkedStyleSheets;

            if (cocktail.ui.globalStyleSheet && this.shadowRoot) {
                linkedSheets = [cocktail.ui.globalStyleSheet, ...linkedSheets];
            }

            if (linkedSheets.length) {
                this.style.visibility = "hidden";
                let loadedSheets = 0;

                let stylesheetLoaded = () => {
                    loadedSheets++;
                    if (loadedSheets == linkedSheets.length) {
                        this.style.visibility = "";
                    }
                }

                for (let uri of linkedSheets) {
                    let link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.addEventListener("load", stylesheetLoaded);
                    link.href = uri;
                    root.appendChild(link);
                }
            }

            // Embedded CSS
            let css = this.constructor.embeddedStyles;
            if (css) {
                let styles = document.createElement('style');
                styles.type = 'text/css';
                styles.textContent = css;
                root.appendChild(styles);
            }
        }

        connectedCallback() {
        }

        disconnectedCallback() {
            this.stopAllObservation();
            this.clearWindowListeners();
        }

        attributeChangedCallback(attrName, oldValue, newValue) {
            let property = this.constructor["_attr_" + attrName];
            if (property && property.reflected && !property.isChanging(this)) {
                let type = property.getType(this);
                if (type) {
                    this[property.name] = type.parseValue(newValue);
                }
            }
        }

        get parentInstance() {
            return this.getRootNode().host;
        }

        addWindowListener(eventType, callback, context = null, options = null) {
            if (!context) {
                context = this;
            }
            let listener = (e) => { return callback.call(context, e); };
            let windowListeners = this[WINDOW_LISTENERS];
            if (!windowListeners) {
                windowListeners = []
                this[WINDOW_LISTENERS] = windowListeners;
            }
            window.addEventListener(eventType, listener, options);
            windowListeners.push([eventType, listener]);
        }

        clearWindowListeners() {
            let windowListeners = this[WINDOW_LISTENERS];
            if (windowListeners) {
                this[WINDOW_LISTENERS] = null;
                for (let [eventType, listener] of windowListeners) {
                    window.removeEventListener(eventType, listener);
                }
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
                cls = class BaseHTMLElement extends componentBase(iface) {};
                cls.linkedStyleSheets = [];
                target[name] = cls;
            }
            return cls;
        }
    });

    cocktail.ui._getObservedAttributes = function (cls) {
        let attributes = [];
        let clsAttributes;
        while (cls) {
            clsAttributes = cls[OBSERVED_ATTRIBUTES];
            if (clsAttributes) {
                attributes.push(...clsAttributes);
            }
            cls = Object.getPrototypeOf(cls);
        }
        return attributes;
    }

    Object.defineProperty(cocktail.ui, "globalStyleSheet", {
        get() {
            if (globalStyleSheet && !globalStyleSheetResolved) {
                globalStyleSheet = cocktail.normalizeResourceURI(globalStyleSheet);
                globalStyleSheetResolved = true;
            }
            return globalStyleSheet;
        },
        set(value) {
            globalStyleSheet = value;
            globalStyleSheetResolved = false;
        }
    });

    cocktail.ui.getShadow = function (element) {
        return element.shadowRoot || element.getRootNode();
    }

    cocktail.ui.descendShadowDOM = function* (node) {
        yield node;

        if (node.shadowRoot) {
            for (let child of node.shadowRoot.childNodes) {
                yield* cocktail.ui.descendShadowDOM(child);
            }
        }

        if (node instanceof HTMLSlotElement) {
            for (let child of node.assignedNodes()) {
                yield* cocktail.ui.descendShadowDOM(child);
            }
        }

        if (node.nodeType == document.ELEMENT_NODE) {
            for (let child of node.childNodes) {
                yield* cocktail.ui.descendShadowDOM(child);
            }
        }
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
        return Boolean(obj[IS_COMPONENT]);
    }

    cocktail.ui.createDisplay = function (display, context) {
        let element = cocktail.ui.isComponent(display) ? display.create() : display();
        Object.assign(element, context);
        return element;
    }

    cocktail.ui.SYNCHRONIZING = Symbol("cocktail.ui.SYNCHRONIZING");

    cocktail.ui.sync = function () {
        const synchronizable = (action) => {

            if (synchronizable[cocktail.ui.SYNCHRONIZING]) {
                return cocktail.ui.SYNCHRONIZING;
            }

            synchronizable[cocktail.ui.SYNCHRONIZING] = true;
            let rvalue;

            try {
                rvalue = action();
            }
            finally {
                delete synchronizable[cocktail.ui.SYNCHRONIZING];
            }

            return rvalue;
        };
        return synchronizable;
    }

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

            if (component[name]) {
                throw new cocktail.ui.PropertyOverrideError(component, name);
            }

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
                component[OBSERVED_ATTRIBUTES].push(this.attributeName);
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

    cocktail.ui.Property.types = {
        string: {
            serializeValue(value) {
                return value === null || value === undefined ? "" : String(value);
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

    cocktail.ui.PropertyOverrideError = class PropertyOverrideError {

        constructor(component, propertyName) {
            this.component = component;
            this.propertyName = propertyName;
        }

        toString() {
            return `Can't override property ${this.propertyName} on ${this.component.fullName}`;
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

    cocktail.ui.getFocusedElement = function () {
        let element;
        for (element of cocktail.ui.iterFocusedPath());
        return element;
    }

    cocktail.ui.iterFocusedPath = function* () {
        let element = document.activeElement;
        do {
            yield element;
            element = element.shadowRoot && element.shadowRoot.activeElement;
        }
        while (element);
    }

    cocktail.ui.isFocused = function (element) {
        for (let node of cocktail.ui.iterFocusedPath()) {
            if (element === node) {
                return true;
            }
        }
        return false;
    }

    const FOCUS_CHECK_DELAY = 200;
    let focusCheck;

    cocktail.ui.focus = function (element) {

        if (focusCheck) {
            clearTimeout(focusCheck);
        }

        function tryToFocus() {
            element.focus();
            if (!cocktail.ui.isFocused(element)) {
                focusCheck = setTimeout(tryToFocus, FOCUS_CHECK_DELAY);
            }
            else {
                focusCheck = null;
            }
        }

        tryToFocus();
    }

    cocktail.ui.setFlag = function (element, attribute, value) {
        if (value) {
            element.setAttribute(attribute, "");
        }
        else {
            element.removeAttribute(attribute);
        }
    }

    cocktail.ui.keys = {
        ENTER: 13,
        ESC: 27,
        BACKSPACE: 8,
        DEL: 46,
        INSERT: 45,
        TAB: 9,
        SHIFT: 16,
        CTRL: 17,
        CAPS_LOCK: 20,
        NUM_LOCK: 144,
        ALT: 18,
        ALTGR: 225,
        UP: 38,
        DOWN: 40,
        LEFT: 37,
        RIGHT: 39,
        HOME: 36,
        END: 35,
        NEXT_PAGE: 34,
        PREV_PAGE: 33,
        MENU: 93,
        F1: 112,
        F2: 113,
        F3: 114,
        F4: 115,
        F5: 116,
        F6: 117,
        F7: 118,
        F8: 119,
        F9: 120,
        F10: 121,
        F11: 122,
        F12: 123
    }

    cocktail.ui.arrowKeys = new Set([
        cocktail.ui.keys.UP,
        cocktail.ui.keys.DOWN,
        cocktail.ui.keys.LEFT,
        cocktail.ui.keys.RIGHT,
    ]);

    cocktail.ui.navigationKeys = new Set([
        ...cocktail.ui.arrowKeys,
        cocktail.ui.keys.HOME,
        cocktail.ui.keys.END,
        cocktail.ui.keys.NEXT_PAGE,
        cocktail.ui.keys.PREV_PAGE
    ]);

    cocktail.ui.functionKeys = new Set([
        cocktail.ui.keys.F1,
        cocktail.ui.keys.F2,
        cocktail.ui.keys.F3,
        cocktail.ui.keys.F4,
        cocktail.ui.keys.F5,
        cocktail.ui.keys.F6,
        cocktail.ui.keys.F7,
        cocktail.ui.keys.F8,
        cocktail.ui.keys.F9,
        cocktail.ui.keys.F10,
        cocktail.ui.keys.F11,
        cocktail.ui.keys.F12
    ]);

    cocktail.ui.nonTextKeys = new Set([
        cocktail.ui.keys.ESC,
        cocktail.ui.keys.INSERT,
        cocktail.ui.keys.TAB,
        cocktail.ui.keys.SHIFT,
        cocktail.ui.keys.CTRL,
        cocktail.ui.keys.CAPS_LOCK,
        cocktail.ui.keys.NUM_LOCK,
        cocktail.ui.keys.ALT,
        cocktail.ui.keys.ALTGR,
        cocktail.ui.keys.MENU,
        ...cocktail.ui.navigationKeys,
        ...cocktail.ui.functionKeys
    ]);
}

