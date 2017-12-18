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
            console.log(error);
            throw error;
        },

        push(state) {
            return this.resolve(state).then((node) => {
                history.pushState({}, "", node.url);
                this.process(node);
            });
        },

        replace(state) {
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
            return this.push(uri.toString());
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

        get parent() {
            return this[PARENT];
        }

        consumePathSegment(path) {
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
                        return null;
                    }
                    return this.resolveChild(path)
                        .then((child) => {
                            if (child) {
                                return child;
                            }
                            return path.length ? null : this;
                        });
                });
        }

        resolveParameters(path) {

            let parameterOrder = [];
            let parameterValues = [];

            for (let i = 0; i < this.parameters.length; i++) {
                let parameter = this.parameters[i];

                // Undefined parameters
                if (i >= path.length) {
                    if (parameter.required) {
                        reject(parameter);
                        break;
                    }
                    else {
                        parameterOrder.push(parameter);
                        parameterValues.push(parameter.getDefault(this));
                    }
                }
                else {
                    // Parse and collect provided parameters
                    parameterOrder.push(parameter);
                    parameterValues.push(parameter.parseValue(path[i]));
                    this.consumePathSegment(path);
                }
            }

            return Promise.all(parameterValues)
                .then((values) => {
                    for (var i = 0; i < values.length; i++) {
                        let parameter = parameterOrder[i];
                        let value = values[i];
                        if (value === undefined) {
                            return false;
                        }
                        this.applyParameter(parameter, value);
                    }

                    // Apply defaults for query string parameters for non terminal nodes
                    if (path.length) {
                        return this.resolveQueryParameters().then(() => true);
                    }

                    return true;
                });
        }

        resolveQueryParameters(queryString = null) {

            if (queryString == "" || queryString == "?") {
                queryString = null;
            }

            this[QUERY_STRING] = queryString;

            let queryParameters = this.queryParameters;
            let queryValues = queryString ? URI(queryString).query(true) : {};
            let parameterOrder = [];
            let parameterValues = [];

            // Supplied values
            // Important: supplied values are applied in the same order they
            // appear in the query string. This behavior can be important on
            // some scenarios, such as preserving arbitrary order when building
            // a list of elements using several different parameters (example:
            // woost.admin.ui.FiltersBar)
            for (let key in queryValues) {
                let value = queryValues[key];
                let parameter = queryParameters[key];
                if (parameter && value !== undefined) {
                    value = parameter.parseValue(value);
                    parameterOrder.push(parameter);
                    parameterValues.push(value);
                }
            }

            // Default values
            for (let key in queryParameters) {
                let parameter = queryParameters[key];
                if (queryValues[key] === undefined) {
                    let value = parameter.getDefaultValue(this);
                    parameterOrder.push(parameter);
                    parameterValues.push(value);
                }
            }

            return Promise.all(parameterValues)
                .then((values) => {
                    for (var i = 0; i < values.length; i++) {
                        let parameter = parameterOrder[i];
                        let value = values[i];
                        this.applyQueryParameter(parameter, value);
                    }
                });
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

cocktail.navigation.StackTransparentNode = class StackTransparentNode extends cocktail.navigation.Node {

    constructor(...args) {
        super(...args);
        let parentStackIndex = this.parent && this.parent.stackIndex;
        this.stackIndex = parentStackIndex === undefined ? -1 : parentStackIndex;
    }
}

cocktail.navigation.StackNode = class StackNode extends cocktail.navigation.Node {

    constructor(...args) {
        super(...args);
        let parentStackIndex = this.parent && this.parent.stackIndex;
        this.stackIndex = parentStackIndex === undefined ? 0 : parentStackIndex + 1;
    }

    traverse() {
        let stack = this.stack;
        let stackNodes = Array.from(stack.iterStack());

        // Remove nodes from the stack
        if (this.stackIndex < stackNodes.length) {
            if (!this.matchesStackNode(stackNodes[this.stackIndex].navigationNode)) {
                stack.pop(stackNodes[this.stackIndex]);
            }
        }

        stackNodes = Array.from(stack.iterStack());

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
        // Update the existing one; only if its the active node
        // (this allows parent nodes to preserve their query string parameters)
        else if (this === cocktail.navigation.node) {
            stackNodes[this.stackIndex].navigationNode = this;
        }
    }

    matchesStackNode(node) {
        return this.pathString == node.pathString;
    }

    activate() {
        // Pop any extra nodes
        let stack = this.stack;
        let stackNodes = Array.from(stack.iterStack());
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

