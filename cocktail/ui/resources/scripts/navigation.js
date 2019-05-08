/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         May 2017
-----------------------------------------------------------------------------*/

{
    const PREFIX = Symbol("cocktail.navigation.PREFIX");
    const PREFIX_COMPONENTS = Symbol("cocktail.navigation.PREFIX_COMPONENTS");

    const getURIForQuery = (newValues) => {
        let changed = false;
        let uri = URI(location.href).query((currentQuery) => {
            let parameters = cocktail.navigation.node.queryParameters;
            for (let key in newValues) {
                let currentValue = currentQuery[key];
                let newValue = newValues[key];
                let parameter = parameters[key];
                if (newValue === undefined) {
                    delete currentQuery[key];
                }
                else {
                    if (parameter) {
                        newValue = parameter.serializeValue(newValue);
                    }
                    currentQuery[key] = newValue;
                }
                changed = changed || (newValue != currentValue);
            }
            return currentQuery;
        });
        return [uri, changed];
    }

    cocktail.navigation = {

        tree: null,
        node: null,
        debug: true,

        get debug() {
            return localStorage.getItem("cocktail.navigation.debug") == "true";
        },

        set debug(value) {
            localStorage.setItem("cocktail.navigation.debug", value ? "true" : "false");
        },

        log(...args) {
            if (this.debug) {
                console.log("cocktail.navigation", ...args);
            }
        },

        logError(...args) {
            if (this.debug) {
                console.error("cocktail.navigation", ...args);
            }
        },

        get prefix() {
            return this[PREFIX];
        },

        set prefix(value) {
            let components = value.replace(/(^\/|\/$)/g, "").split("/");
            this[PREFIX] = "/" + components.join("/") + (components.length ? "/" : "");
            this[PREFIX_COMPONENTS] = components;
        },

        get prefixComponents() {
            return this[PREFIX_COMPONENTS];
        },

        process(state) {
            return this.resolve(state).then((node) => {
                if (node) {
                    this.node = node;
                    for (let pathNode of node.fromRoot()) {
                        pathNode.traverse();
                    }
                    node.activate();
                    cocktail.ui.trigger(window, "navigationNodeChanged");
                }
            });
        },

        resolve(state) {

            if (state instanceof cocktail.navigation.Node) {
                return Promise.resolve(state);
            }

            let uri = URI(state);
            let pathName = uri.pathname();
            let path;

            if (!pathName.length) {
                path = [];
            }
            else if (pathName.charAt(0) == "/") {
                path = uri.segment();
            }
            else {
                path = uri.absoluteTo(location.href).segment();
            }

            if (path.length == 1 && !path[0]) {
                path = [];
            }

            for (let i = 0; i < this[PREFIX_COMPONENTS].length; i++) {
                if (i >= path.length || path[i] != this[PREFIX_COMPONENTS][i]) {
                    throw new cocktail.navigation.NavigationError(`${state} doesn't match the application's URL prefix ${this[PREFIX]}`);
                }
            }

            path = path.slice(this[PREFIX_COMPONENTS].length);

            return this.tree.resolve(path)
                .then((node) => {
                    if (!node) {
                        throw new cocktail.navigation.NavigationError(`Can't resolve ${path}`);
                    }
                    return node.resolveQueryParameters(uri.search()).then(() => node);
                })
                .catch((error) => this.handleError(error));
        },

        handleError(error) {
            this.logError(error);
            throw error;
        },

        push(state) {
            this.log("pushing state", state);
            return this.resolve(state).then((node) => {
                history.pushState({}, "", node.url);
                this.log(`processing URL ${node.url}`);
                this.process(node);
            });
        },

        replace(state) {
            this.log("replacing state", state);
            return this.resolve(state).then((node) => {
                history.replaceState({}, "", node.url);
                this.process(node);
            });
        },

        up() {
            if (!this.node || !this.node.parent) {
                throw new cocktail.navigation.NavigationError("There is no parent state to go back to");
            }
            return this.push(this.node.parent);
        },

        extendPath(...segments) {
            let uri = URI(location.href).query("");
            uri = uri.segment([...uri.segment(), ...Array.from(segments, (segment) => segment.toString())]);
            return this.push(uri.normalizePath().toString());
        },

        changeQuery(newValues) {
            let [uri, changed] = getURIForQuery(newValues);
            return changed ? this.push(uri.toString()) : Promise.resolve(cocktail.navigation.node);
        },

        replaceQuery(newValues) {
            let [uri, changed] = getURIForQuery(newValues);
            return changed ? this.replace(uri.toString()) : Promise.resolve(cocktail.navigation.node);
        }
    }

    cocktail.navigation.prefix = "/";
}

{
    const PARENT = Symbol("cocktail.navigation.Node.PARENT");
    const PATH = Symbol("cocktail.navigation.Node.PATH");
    const CHILDREN = Symbol("cocktail.navigation.Node.CHILDREN");
    const WILDCARDS = Symbol("cocktail.navigation.Node.WILDCARDS");
    const PARAMETERS = Symbol("cocktail.navigation.Node.PARAMETERS");
    const QUERY_STRING = Symbol("cocktail.navigation.Node.QUERY_STRING");
    const QUERY_PARAMETERS = Symbol("cocktail.navigation.Node.QUERY_PARAMETERS");

    cocktail.navigation.Node = class Node {

        constructor(parent = null) {
            this[PARENT] = parent;
            this[PATH] = [];
        }

        toString() {
            return `${this.constructor.name}("${this.pathString}")`;
        }

        get parent() {
            return this[PARENT];
        }

        consumePathSegment(path, reason = null) {
            if (!path.length) {
                throw "Can't consume a segment from an empty path";
            }
            cocktail.navigation.log(`${this.constructor.name} consumed segment "${path[0]}" (${reason || "custom resolution"})`);
            this[PATH].push(path.shift());
        }

        get path() {
            let path = [...this[PATH]];
            if (this[PARENT]) {
                path = [...this[PARENT].path, ...path];
            }
            return path;
        }

        get pathString() {
            return cocktail.navigation.prefix + this.path.join("/");
        }

        get consumedPath() {
            return this[PATH];
        }

        get queryString() {
            return this[QUERY_STRING];
        }

        *towardsRoot() {
            let node = this;
            do {
                yield node;
                node = node[PARENT];
            }
            while (node);
        }

        *fromRoot() {
            if (this[PARENT]) {
                for (let ancestor of this[PARENT].fromRoot()) {
                    yield ancestor;
                }
            }
            yield this;
        }

        get url() {
            let url = cocktail.navigation.prefix + this.path.join("/");
            if (this[QUERY_STRING]) {
                url += this[QUERY_STRING];
            }
            return url;
        }

        static get parameters() {
            return [];
        }

        defineParameters() {
            return this.constructor.parameters;
        }

        get parameters() {
            if (!this[PARAMETERS]) {
                this[PARAMETERS] = this.defineParameters();
            }
            return this[PARAMETERS];
        }

        static get queryParameters() {
            return [];
        }

        defineQueryParameters() {
            return this.constructor.queryParameters;
        }

        get queryParameters() {
            if (!this[QUERY_PARAMETERS]) {
                let parameters = {};
                for (let parameter of this.defineQueryParameters()) {
                    parameters[parameter.name] = parameter;
                }
                this[QUERY_PARAMETERS] = parameters;
            }
            return this[QUERY_PARAMETERS];
        }

        static get children() {
            return {};
        }

        get children() {
            if (!this[CHILDREN]) {
                this[CHILDREN] = this.constructor.children;
            }
            return this[CHILDREN];
        }

        static get wildcards() {
            return [];
        }

        get wildcards() {
            if (!this[WILDCARDS]) {
                this[WILDCARDS] = this.constructor.wildcards;
            }
            return this[WILDCARDS];
        }

        static resolve(path, parentNode, segment = null) {

            let remainingPath = Array.from(path);
            let node = parentNode ? parentNode.createChild(this) : new this();

            if (segment) {
                cocktail.navigation.log(`${this.name} consumed segment "${segment}" (regular child)`);
                node[PATH].push(segment);
            }

            return node.resolvePath(remainingPath);
        }

        createChild(nodeClass) {
            return new nodeClass(this);
        }

        resolvePath(path) {
            return this.resolveParameters(path)
                .then((valid) => {
                    if (!valid) {
                        cocktail.navigation.logError("Invalid parameters");
                        return null;
                    }
                    return this.resolveChild(path)
                        .then((child) => {
                            if (child) {
                                return child;
                            }
                            if (path.length) {
                                cocktail.navigation.logError("Unprocessed path segments remaining", path);
                            }
                            return path.length ? null : this;
                        });
                });
        }

        async resolveParameters(path) {

            for (let i = 0; i < this.parameters.length; i++) {
                const parameter = this.parameters[i];

                // Defined parameters
                if (i < path.length) {
                    const value = await parameter.parseValue(path[i]);
                    this.applyParameter(parameter, value);
                    this.consumePathSegment(path, "parameter " + parameter.name);
                }
                // Undefined parameters (segments missing)
                else {
                    if (parameter.required) {
                        reject(parameter);
                        break;
                    }
                    else {
                        const value = await parameter.getDefaultValue(this);
                        this.applyParameter(parameter, value);
                    }
                }
            }

            // Apply defaults for query string parameters for non terminal nodes
            if (path.length) {
                return this.resolveQueryParameters().then(() => true);
            }

            return true;
        }

        async resolveQueryParameters(queryString = null) {

            if (queryString == "" || queryString == "?") {
                queryString = null;
            }

            this[QUERY_STRING] = queryString;

            let queryParameters = this.queryParameters;
            let queryValues = queryString ? URI(queryString).query(true) : {};

            for (let key in this.queryParameters) {
                const parameter = this.queryParameters[key];
                let value = queryValues[parameter.name];
                if (value === undefined) {
                    value = await parameter.getDefaultValue();
                }
                else {
                    value = await parameter.parseValue(value);
                }
                this.applyQueryParameter(parameter, value);
            }
        }

        resolveChild(path) {

            let childResolution;

            if (path.length) {
                let segment = path[0];
                let childClass = this.children[segment];
                if (childClass) {
                    childResolution = childClass.resolve(path.slice(1), this, segment);
                }
            }

            return (childResolution || Promise.resolve(null)).then((child) => {

                if (child) {
                    return child;
                }

                let findFirstMatchingWildcard = (i) => {
                    if (i == this.wildcards.length) {
                        return null;
                    }
                    return this.wildcards[i].resolve(path, this)
                        .then((child) => {
                            return child || findFirstMatchingWildcard(i + 1);
                        });
                };

                return findFirstMatchingWildcard(0);
            });
        }

        applyParameter(parameter, value) {
            this[parameter.name] = value;
        }

        applyQueryParameter(parameter, value) {
            this[parameter.name] = value;
        }

        traverse() {
        }

        activate() {
        }
    }
}

cocktail.navigation.StackNode = class StackNode extends cocktail.navigation.Node {

    constructor(...args) {
        super(...args);
        let parentStackIndex = this.parent && this.parent.stackIndex;
        const offset = this.createsStackUI ? 0 : -1;
        this.stackIndex = parentStackIndex === undefined ? offset : parentStackIndex + offset + 1;
    }

    get createsStackUI() {
        return true;
    }

    traverse() {

        if (!this.createsStackUI) {
            return;
        }

        let stack = this.stack;
        const getNodes = () => Array.from(stack.iterStack()).filter((node) => node.animationState != "closing");
        let stackNodes = getNodes();

        // Remove nodes from the stack
        if (this.stackIndex < stackNodes.length) {
            if (!this.matchesStackNode(stackNodes[this.stackIndex].navigationNode)) {
                stack.pop(stackNodes[this.stackIndex]);
            }
        }

        stackNodes = getNodes();

        // Add a new node to the stack
        if (
            this.stackIndex >= stackNodes.length
            || !this.matchesStackNode(stackNodes[this.stackIndex].navigationNode)
        ) {
            let stackNode = this.createStackNode();
            this.stackNode = stackNode;
            stackNode.navigationNode = this;
            stack.push(stackNode);
        }
        // Update the existing one
        else {
            const stackNode = stackNodes[this.stackIndex];
            this.stackNode = stackNode;

            // Update the navigationNode property of the UI, only for the stack's top node
            // (this allows parent nodes to preserve their query string parameters)
            if (this === cocktail.navigation.node) {
                stackNode.navigationNode = this;
            }
        }
    }

    matchesStackNode(node) {
        return this.pathString == node.pathString;
    }

    activate() {
        // Pop any extra nodes
        let stack = this.stack;
        let stackNodes = Array.from(stack.iterStack()).filter((node) => node.animationState != "closing");
        if (stackNodes.length > this.stackIndex + 1) {
            stack.pop(stackNodes[this.stackIndex + 1]);
        }
    }

    get stack() {
        return cocktail.ui.root.stack;
    }

    createStackNode() {
        throw `No view specified for ${this}`;
    }
}

cocktail.navigation.PathResolutionError = class PathResolutionError {

    constructor(nodeClass, path) {
        this.nodeClass = nodeClass;
        this.path = path;
    }

    toString() {
        return `${this.nodeClass.name} can't resolve path ${this.path.join("/")}`;
    }
}

cocktail.navigation.NavigationError = class NavigationError {

    constructor(message) {
        this.message = message;
    }

    toString() {
        return this.message;
    }
}

{
    let processCurrentLocation = (e) => {
        cocktail.ui.rootReady.then(() => {
            if (cocktail.navigation.tree) {
                cocktail.navigation.process(location.href);
            }
        });
    }

    window.addEventListener("DOMContentLoaded", processCurrentLocation);
    window.addEventListener("popstate", processCurrentLocation);
}

