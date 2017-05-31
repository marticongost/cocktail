/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         May 2017
-----------------------------------------------------------------------------*/

{
    const TREE = Symbol("cocktail.navigation.Navigation.TREE");

    cocktail.navigation = {

        tree: null,

        process(state) {
            this.node = this.resolve(state);
            for (let node of this.node.fromRoot()) {
                node.traverse();
            }
            this.node.activate();
        },

        resolve(state) {
            if (typeof(state) == "string") {
                let path = URI(state).segment();
                if (path.length == 1 && !path[0]) {
                    path = [];
                }
                state = this.tree.resolve(path);
                if (!state) {
                    this.handleError(new cocktail.navigation.PathResolutionError(this.tree, path));
                }
            }
            return state;
        },

        handleError(error) {
            throw error;
        },

        push(state) {
            state = this.resolve(state);
            history.pushState({}, "", state.url);
            this.process(state);
        },

        replace(state) {
            state = this.resolve(state);
            history.replaceState({}, "", state.url);
            this.process(state);
        },

        up() {
            if (!this.node || !this.node.parent) {
                throw new cocktail.navigation.NavigationError("There is no parent state to go back to");
            }

            this.push(this.node.parent);
        },

        extendPath(...segments) {
            this.push(location.href + "/" + segments.join("/"));
        }
    }
}

{
    const PARENT = Symbol("cocktail.navigation.Node.PARENT");
    const PATH = Symbol("cocktail.navigation.Node.PATH");
    const CHILDREN = Symbol("cocktail.navigation.Node.CHILDREN");
    const WILDCARDS = Symbol("cocktail.navigation.Node.WILDCARDS");
    const PARAMETERS = Symbol("cocktail.navigation.Node.PARAMETERS");

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

        get consumedPath() {
            return this[PATH];
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
            return "/" + this.path.join("/");
        }

        static get parameters() {
            return [];
        }

        get parameters() {
            if (!this[PARAMETERS]) {
                this[PARAMETERS] = this.constructor.parameters;
            }
            return this[PARAMETERS];
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

        static requireResolution(path) {
            let node = this.resolve(path);
            if (!node) {
                throw new cocktail.navigation.PathResolutionError(this, path);
            }
            return node;
        }

        static resolve(path, parentNode, segment = null) {

            let remainingPath = Array.from(path);
            let node = new this(parentNode);

            if (segment) {
                node[PATH].push(segment);
            }

            if (!node.resolveParameters(remainingPath)) {
                return null;
            }

            let descendant = node.resolveChild(remainingPath);
            if (descendant) {
                return descendant;
            }

            return remainingPath.length ? null : node;
        }

        resolveParameters(path) {

            for (let i = 0; i < this.parameters.length; i++) {
                let parameter = this.parameters[i];

                // Undefined parameters
                if (i >= path.length) {
                    if (parameter.required) {
                        return false;
                    }
                    else {
                        this.applyParameter(parameter, parameter.getDefault(this));
                    }
                }
                else {
                    // Parse and collect provided parameters
                    let value = parameter.parseValue(path[i]);
                    if (value === undefined) {
                        return false;
                    }
                    // TODO: parameter validation rules
                    this.applyParameter(parameter, value);
                    this.consumePathSegment(path);
                }
            }

            return true;
        }

        resolveChild(path) {

            if (path.length) {
                let segment = path[0];
                let childClass = this.children[segment];
                if (childClass) {
                    let descendant = childClass.resolve(path.slice(1), this, segment);
                    if (descendant) {
                        return descendant;
                    }
                }
            }

            for (let wildcardClass of this.wildcards) {
                let descendant = wildcardClass.resolve(path, this);
                if (descendant) {
                    return descendant;
                }
            }

            return null;
        }

        applyParameter(parameter, value) {
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
        this.stackIndex = parentStackIndex === undefined ? 0 : parentStackIndex + 1;
    }

    traverse() {
        let stack = this.stack;
        let stackNodes = Array.from(stack.iterStack());
        let url = this.url;
        let waitForAnimation;

        // Remove nodes from the stack
        if (this.stackIndex < stackNodes.length) {
            if (stackNodes[this.stackIndex].url != url) {
                waitForAnimation = stack.popAndWait(stackNodes[this.stackIndex]);
            }
        }

        if (!waitForAnimation) {
            waitForAnimation = Promise.resolve(null);
        }

        // Add a new node to the stack
        waitForAnimation.then(() => {
            stackNodes = Array.from(stack.iterStack());
            if (this.stackIndex >= stackNodes.length || stackNodes[this.stackIndex].url != url) {
                let stackNode = this.createStackNode();
                stackNode.url = url;
                stack.push(stackNode);
            }
        });
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

