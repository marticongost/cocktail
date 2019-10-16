/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         April 2017
-----------------------------------------------------------------------------*/

{
    const ID = Symbol("cocktail.ui.Action.ID");
    const ENABLED = Symbol("cocktail.ui.Action.ENABLED");

    cocktail.ui.ActionSource = class ActionNode {

        constructor(id, parameters = null) {
            this[ID] = id;
            this.component = null;
            if (parameters) {
                Object.assign(this, parameters);
            }
        }

        get id() {
            return this[ID];
        }

        createUI(context = null) {
            const component = this.getComponent(context);
            const element = component.create();
            element.actionSource = this;
            return element;
        }

        getComponent(context) {
            let component = this.component || context.defaultComponent || this.constructor.defaultComponent;
            return component.create ? component : component();
        }

        static get defaultComponent() {
            return null;
        }

        get translationPrefix() {
            return "cocktail.ui.actions";
        }

        get translationKey() {
            return `${this.translationPrefix}.${this.id}`;
        }

        translate(context) {
            return cocktail.ui.translations[this.translationKey];
        }

        static get enabled() {
            const enabled = this[ENABLED];
            return enabled === undefined ? true : enabled;
        }

        static set enabled(value) {
            this[ENABLED] = value;
        }

        get enabled() {
            const enabled = this[ENABLED];
            return enabled === undefined ? this.constructor.enabled : enabled;
        }

        set enabled(value) {
            this[ENABLED] = value;
        }

        compatibleWith(context) {
            return this.enabled;
        }
    }
}

{
    const ACTION_MAP = Symbol();
    const ACTION_LIST = Symbol();

    cocktail.ui.ActionSet = class ActionSet extends cocktail.ui.ActionSource {

        constructor(id, parameters = null) {

            const entries = parameters.entries;
            delete parameters.entries;
            super(id, parameters);

            this[ACTION_MAP] = {};
            this[ACTION_LIST] = [];

            if (entries) {
                for (let entry of entries) {
                    this.add(entry);
                }
            }
        }

        static get defaultComponent() {
            return cocktail.ui.ActionList.withProperties({buttonStyle: "auto"});
        }

        getEntry(id) {
            return this[ACTION_MAP][id];
        }

        entries(context = null) {
            if (context) {
                return Array.from(this[ACTION_LIST].filter((entry) => entry.compatibleWith(context)));
            }
            else {
                return Array.from(this[ACTION_LIST]);
            }
        }

        add(entry, options = null) {
            const order = options && options.order;

            if (this[ACTION_MAP][entry.id]) {
                throw new cocktail.ui.ActionRegistrationError(`An action with id ${entry.id} already exists on ${this}`);
            }

            if (order === null || order === undefined) {
                this[ACTION_LIST].push(entry);
            }
            else if (typeof(order) == "string") {
                let placement, anchorId;
                try {
                    [placement, anchorId] = order.split(" ");
                }
                catch (e) {
                    throw new cocktail.ui.ActionRegistrationError(
                        `"${order}" is not a valid order string; expected "before ACTION_ID" or "after ACTION_ID"`
                    );
                }

                const anchor = this[ACTION_MAP][anchorId];
                if (!anchor) {
                    throw new cocktail.ui.ActionRegistrationError(
                        `Invalid anchor "${anchorId}"; no action with that ID exists on ${this}`
                    );
                }

                let anchorIndex = this[ACTION_LIST].indexOf(anchor);
                if (placement == "after") {
                    anchorIndex++;
                }
                else if (placement != "before") {
                    throw new cocktail.ui.ActionRegistrationError(
                        `Invalid placement "${placement}"; expected "after" or "before"`
                    );
                }

                this[ACTION_LIST].splice(anchorIndex, 0, entry);
            }
            else {
                throw new cocktail.ui.ActionRegistrationError(
                    `Invalid order "${order}", expected null or a string`
                );
            }

            this[ACTION_MAP][entry.id] = entry;
            return entry;
        }
    }
}

{
    cocktail.ui.Action = class Action extends cocktail.ui.ActionSource {

        static get defaultComponent() {
            return cocktail.ui.ActionListButton;
        }

        get min() {
            return null;
        }

        get max() {
            return null;
        }

        getIconURL(context) {
            return null;
        }

        getShortcut(context) {
            return cocktail.ui.translations[this.translationKey + ".shortcut"];
        }

        getState(context) {

            let selectionSize = context.selection.length;

            let min = this.min;
            if (min !== null && selectionSize < min) {
                return "disabled";
            }

            let max = this.max;
            if (max !== null && selectionSize > max) {
                return "disabled";
            }

            return "visible";
        }

        invoke(context) {
        }
    }
}

cocktail.ui.ActionRegistrationError = class ActionRegistrationError {

    constructor(message) {
        this.message = message;
    }

    toString() {
        return this.message;
    }
}

